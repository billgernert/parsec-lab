# The Self-Service Server Build Pipeline

*One click to provision a fully configured, monitored, domain-joined VM from nothing, and cleanly tear it back down.*

---

## The Problem

Building a server by hand was never one hard task. It was a dozen small ones, and the trouble lived in the gaps between them.

At work we had good pieces to start from. There was a script to install the Zabbix agent and secure it with a unique PSK. We kept a set of VM templates. We had documentation. But the templates were patched manually every month, so a missed cycle meant a new server came up already behind on updates, sometimes with reboot problems waiting to happen. The documentation drifted out of date as we adopted new systems and procedures. Backup tags were set by hand, so they got missed or set wrong. And IPAM was a race: the IP you reserved might already be taken by the time your server was actually ready.

None of it was unbearable. I can multitask, and I could usually get a build done fairly quickly. But "quickly" still meant waiting on the security team to configure the SIEM and the ITSM team to register the box in our service management system. Every server touched several teams and several manual steps, and every manual step was a chance for drift and misconfiguration.

Decommissioning was worse. Steps got skipped. Static IPs were left stranded. Firewall rules were the real danger. Deleting microsegmentation rules incorrectly could leave an ANY/ANY rule wide open, and once an entire rule set was removed by accident and took down a whole environment. A missed cleanup step wasn't just messy, it could cause an outage.

The pressure showed up worst during the crunch cycles. Several Windows Server versions hit end of life around the same time, and those migration projects meant standing up a lot of machines fast. Or a team would need a server today, the template would have a problem, and suddenly the whole thing had to be built from scratch under a deadline.

The manual process worked, mostly, because good people made it work. But it didn't scale, it drifted, and it left room for expensive mistakes. That's the problem I wanted to solve in my lab: take the entire lifecycle, from "I need a server" to "it's gone and cleaned up," and make it one repeatable, auditable, hands-off process.

---

## What I Built

A self-service server build pipeline with a simple front end. You fill in a short form: server name, resources, operating system, any extra disk, and a checkbox list of the ten most common applications and the ten most common Windows roles and features. You submit it, and the request goes to an approval workflow. The approver clicks once, and a few minutes later a fully built server is waiting.

Not a bare VM. A server that's domain joined, fully updated, secured, monitored, and ready to hand off. What used to be a chain of manual steps across several teams is now a form and an approval, start to finish in under ten minutes.

And when the server's life is over, the same system tears it back down cleanly: the VM, its IP reservation, its monitoring registration, all of it, with none of the stranded leftovers that used to cause problems.

---

## How It Works

The pipeline runs in fifteen stages. I'll group them into five phases so the flow is easy to follow, and I'll explain the jargon as we go.

One thing to know up front: almost none of this runs on a fixed server. When the pipeline starts, **Jenkins** (the automation server that orchestrates everything) asks **Kubernetes** (the system that runs containers) to spin up a temporary worker called a **pod**. That pod is stateless: it does its job and gets destroyed. The pod image was pre-built with **Kaniko** (a tool that builds container images inside Kubernetes) so all the tools I need are already baked in and ready. Jenkins injects credentials into the pod at creation time, scoped to least privilege, so each run only has the access it needs and nothing lingers afterward. Nothing is left running, nothing holds long-lived secrets.

### Phase 1: Reserve and place

**Stage 1 - Allocate an IP.** The pipeline asks **NetBox**, my IPAM (IP Address Management) tool and single source of truth for the network, to reserve the next free address in the right prefix. This kills the old race condition where the IP you picked was taken by the time your server was ready. NetBox hands back the address, and from that I derive a collision-free **Proxmox VM ID** and the gateway. (Proxmox is the virtualization platform running the actual VMs.)

**Stage 2 - Pick the best node.** The cluster has multiple physical nodes. The pipeline ranks the online ones by free memory and runs a disk pre-flight check sized to the request, so the VM lands on a host that can actually hold it. No more guessing which node has room.

### Phase 2: Prepare

**Stage 3 - Generate a local admin password.** The pipeline logs in to **Vault** (HashiCorp's secrets manager) using **AppRole** (a machine-to-machine login method, no human passwords involved) and generates a unique local Administrator password for this specific host, stored safely in Vault. Every server gets its own password. Nothing is reused, nothing is hardcoded.

**Stage 4 - Resolve the template.** A small script looks up the tagged VM template for the requested OS and returns its ID and location. Templates are golden images I keep patched and ready, so a new build starts from a known-good baseline instead of a fresh install.

**Stage 5 - Terraform Plan.** **Terraform** (the Infrastructure as Code tool that defines infrastructure in version-controlled files) generates a *plan*: a precise, readable description of exactly what it's about to create. Each build gets its own isolated workspace so concurrent builds never step on each other. Critically, this is only the plan. Nothing has been built yet.

### Phase 3: Approve

**Stage 6 - The approval gate.** The pipeline pauses and sends an HTML email with the VM's details and a deep link straight to the approval screen. The approver reviews what's about to be built and clicks **Apply** or **Abort**.

This placement is deliberate. You're not rubber-stamping a blank request, you're approving the actual plan, with the real resources, IP, and configuration laid out in front of you. Approve with confidence, or abort before anything exists.

### Phase 4: Build

**Stage 7 - Terraform Apply.** On approval, Terraform full-clones the template to the chosen node, applies a **cloud-init** drive (a standard way to hand a VM its first-boot settings: static IP, gateway, DNS), and boots it. Then it clears the template tags the clone inherited, using the Proxmox API, so the new VM isn't mistaken for a template.

**Stages 8-9 - Register monitoring and wait for the VM.** The pipeline registers the host in **Zabbix** (the monitoring system) with a unique **PSK** (pre-shared key, so the agent and server trust each other over an encrypted channel), then polls the VM until **WinRM** (Windows Remote Management, the channel Ansible uses to configure Windows) is up and answering. It doesn't move on until the machine is genuinely ready.

**Stages 10-12 - Disk work.** If the OS disk needs to be bigger than the template's, the pipeline grows it through the Proxmox API. If the request asked for fast local **NVMe** storage, it live-migrates the disk to node-local storage with no downtime to the guest. If a separate data disk was requested, it attaches one. All of this is transparent to the running VM.

### Phase 5: Configure and finish

**Stage 13 - Configure with Ansible.** This is where the bare VM becomes a real server. **Ansible** (the configuration tool that enforces desired state) runs through an ordered set of roles: rotate the password, expand the C: drive inside the guest, rename and domain-join the machine into the right OU, install the Zabbix agent, set time sync, configure the firewall, set up **Duo MFA** (multi-factor authentication on RDP logins, keys pulled from Vault, set to fail-open if Duo is unreachable so I'm never locked out), then install the requested applications, Windows roles and features, and initialize the data disk. Every secret in this stage comes from Vault. Nothing is stored in the pipeline.

**Stage 14 - Register DNS.** The pipeline creates the forward (A) and reverse (PTR) DNS records on the domain controller, and optionally publishes a public record too. The record creation is idempotent, meaning running it twice causes no harm, it just ensures the record exists.

**Stage 15 - Notify and clean up.** On success, it emails the requester that the server is ready. On failure, it conditionally releases the NetBox IP it reserved back at the start, so a failed build doesn't strand an address. That single cleanup step is a direct answer to one of the worst parts of the old manual process.

---

## Key Decisions

A pipeline is really a stack of choices. Here are the ones that mattered most and why I made them.

**Put the approval gate after the plan, not before.** The approval sits right after Terraform generates its plan and right before anything gets built. That timing is the whole point. By then the IP is allocated, the node is chosen, and the template is resolved, so the approver has real data to look at and can verify all of it. They can reasonably infer the build won't fail from here. It's the point of no return, and I wanted a human looking at the real details at exactly that moment, not rubber-stamping a blank request up front.

**Never reuse a credential.** Every host gets its own local admin password and its own monitoring PSK, all stored in Vault. This is a simple security principle with a big payoff: with shared passwords, if one credential is compromised, they all are. Giving each host its own eliminates an entire attack vector. It's one layer in a broader defense-in-depth approach, but it's a layer that costs almost nothing and closes a real hole.

**Build on stateless, disposable pods.** Instead of a permanent build server, every run spins up a fresh Kubernetes pod that does its job and gets destroyed. This is exactly what Kubernetes and Kaniko were built for. Every build runs in an identical environment, so nothing drifts the way a long-lived static agent inevitably does. The pods start up fast, remember nothing between runs, and I can spin up as many as my resources allow. A static agent can't do that, and a static agent that slowly drifts is its own security weakness. Disposable removes the whole problem.

**Fail open on MFA.** Duo MFA on RDP is set to fail open: if Duo is unreachable, the login still goes through. That's a deliberate tradeoff of strict enforcement for availability, and I made it on purpose. Getting locked out is a real risk, and anyone who has ever hit an emergency and couldn't get in to troubleshoot understands why. There are other layered security controls backing this up, so failing open here doesn't leave the door wide open. It just makes sure I can always get to the box when it matters. That said, fail-open is where I'm starting, not where I intend to end. Once I've run it long enough to trust the Duo integration and my fallback access paths under real conditions, the plan is to tighten it toward fail-closed, so the default becomes strict enforcement with well-tested break-glass access rather than an open door.

**Resolve templates by tag, not by hardcoded ID.** The pipeline finds the right template by its tag instead of a fixed VM ID. This lets me keep a backup template sitting ready at all times. The tag only moves to a new template once that template is built and verified, so if a new build of the template ever fails, the old one is still there and still tagged. No downtime, no renumbering, and always a known-good fallback.

---

## Lessons Learned

**The templates were the hardest part, and they lived in a different pipeline entirely.** Before this provisioning pipeline could exist, I needed golden images that were reliably patched and ready. That turned out to be the real fight.

My first plan was the obvious one: power on each template monthly, let it patch, sysprep it, and shut it back down. It didn't hold up. Sysprep has a hard limit on how many times you can rearm an image, and I kept hitting rearm issues and repeated failures. What looked like a simple maintenance loop turned into a fragile process that broke in ways that were painful to recover from.

The fix was to stop reusing one image over and over. Instead I build several custom Windows images and let them install updates on a weekly schedule, and the template tag only moves to the new image once it's built and verified. That change made the whole thing stable and reliable, and just as importantly, it removed downtime completely. There's always a known-good template tagged and ready, so patching a template never takes the pipeline offline. Downtime was a deal breaker for me, and designing around it is what finally made the templates trustworthy.

**A few smaller lessons from the provisioning pipeline itself:**

- **Clones inherit template tags.** When Terraform full-clones a template, the new VM comes up carrying the template's tags. If I didn't strip them, a provisioned server could be mistaken for a template. The pipeline clears them through the Proxmox API right after apply, so only real templates ever carry template tags.

- **Proxmox doesn't hand the guest a hostname.** The configdrive2 that cloud-init reads has no hostname field, so the machine boots with a generic name. The rename has to happen in Ansible, and it has to happen *before* the domain join, or the computer joins AD under the wrong name.

- **Keep the local-admin password even after decommission.** Early on I deleted a host's Vault secrets when it was decommissioned. Then I restored a VM from a PBS backup and couldn't log in, because its per-host password was gone. Now the pipeline retains the local-admin password in Vault on decommission, so a restored VM is always reachable.

- **Validate input as early as possible.** My server-name validation runs in the pipeline, but it really belongs in the webform. A simple regex on the form (max 15 characters, no spaces) would catch a bad name before the pipeline ever starts. It's on my list to move.

The theme across all of these is the same: the failure modes only show up once real builds start hitting real edge cases, and the fixes are usually about designing so the failure can't happen again, rather than just handling it when it does.

---

## What's Next

This pipeline works, but it's never really finished. A few things I'm planning or already building:

- **Move input validation into the webform.** Catch bad server names with a simple regex before the pipeline ever starts, instead of validating after the fact.

- **Record a per-host manifest.** Capture each server's exact configuration (its apps, roles, disks, and options) in version control at build time, so a rebuild or a restore reconciles back to the real desired state instead of guessing.

- **Tighten MFA toward fail-closed** once the Duo integration and fallback access have been tested under real conditions.

- **Extend the same pattern to Linux and to the cloud.** The provisioning model isn't Windows-specific. The same reserve-plan-approve-build-configure flow already applies to my Linux builds, and the next step is pointing it at AWS so the same one-click experience works across on-prem and cloud.

- **Self-service without me in the loop.** Right now it's a form and an approval. The goal is a proper self-service portal where a team can request a server, have it approved, and have it delivered without anyone touching the pipeline by hand.

The through-line for all of it is the same idea that started the project: take something that used to be manual, fragile, and slow, and turn it into something repeatable, auditable, and boring, in the best possible way.

> **The live, stage-by-stage version of this pipeline** is at
> [parsec-lab.com/projects](https://parsec-lab.com/projects/), alongside the other pipelines that run
> this lab and the bugs that shaped them. The architecture it all runs on is at
> [parsec-lab.com/diagram](https://parsec-lab.com/diagram/).
