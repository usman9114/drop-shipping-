# Runbook: Postgres on a VPS, reached by CI through an SSH tunnel

> Status: **draft, not yet run on a real server.** Run it first on a throwaway VPS and fix whatever differs. You run these steps; Claude does not get access to the server and never sees its passwords or keys.
> Decision: `docs/decisions/0004-postgres-warehouse-and-source-terms.md` (hosting amended: VPS).
> Where a step is standard but I could not verify the exact current syntax, it says so. Follow the official docs linked in each step when they differ.

## 0. What you are building

```
GitHub Actions job                                   Your VPS (Ubuntu LTS)
  ssh -L 5432:127.0.0.1:5432  ── encrypted ──▶   sshd: user "tunnel", key can ONLY forward to 127.0.0.1:5432
  dbmate / ingest / dbt  ──▶ localhost:5432                │
                                                           ▼
                                              Docker: postgres:17, bound to 127.0.0.1 only
                                              firewall: only SSH (22) open to the internet
```

No database port is exposed to the internet. GitHub runner IP ranges are too large to allow-list, which is why the tunnel is used instead.

## 1. Choose the server

| Item | Suggestion |
|---|---|
| OS | Ubuntu 24.04 LTS (or Debian stable) |
| Size | 1-2 vCPU, **2 GB RAM**, 40 GB SSD. Our data is small; RAM and disk for backups matter more. |
| Region | US (our market; also close to GitHub's US runners) |
| Extras | Provider snapshots or backups if cheap. Enable the provider's firewall too, as a second layer. |

Providers differ on price and quality; compare a few before buying. I have not researched them.

## 2. Harden the server (one time, as root, from your laptop)

Keep one SSH session open while you test a second, so a mistake does not lock you out.

1. Create a normal admin user and give it your public key:
   `adduser deploy`, `usermod -aG sudo deploy`, then append your public key to `/home/deploy/.ssh/authorized_keys` (mode 600, directory 700).
2. Confirm you can log in as `deploy` with the key, in a new terminal.
3. Disable root login and passwords. Create `/etc/ssh/sshd_config.d/10-hardening.conf` containing:
   ```
   PermitRootLogin no
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   ```
   then `sudo sshd -t && sudo systemctl reload ssh`.
4. Firewall: `sudo ufw default deny incoming`, `sudo ufw allow OpenSSH`, `sudo ufw enable`.
5. Automatic security updates and brute-force protection: `sudo apt install unattended-upgrades fail2ban`, then `sudo dpkg-reconfigure -plow unattended-upgrades`.

## 3. Install Docker

Use Docker's official apt repository, following https://docs.docker.com/engine/install/ubuntu/ (do not pipe an install script into a shell). Add `deploy` to the `docker` group, or use sudo.

## 4. Start Postgres

On the server, as `deploy`:

```bash
sudo mkdir -p /opt/warehouse/secrets && sudo chown -R deploy: /opt/warehouse
cd /opt/warehouse
# copy infra/vps/docker-compose.yml from this repo to /opt/warehouse/
umask 077
openssl rand -base64 32 > secrets/pg_owner_password
docker compose up -d
docker compose ps          # should show "healthy" after a few seconds
```

Store the owner password in your password manager. It is used for migrations only.

Check it listens locally only: `ss -ltnp | grep 5432` should show `127.0.0.1:5432`, not `0.0.0.0`.

## 5. The CI tunnel user (can do nothing except forward one port)

On the server:

```bash
sudo adduser --disabled-password --gecos "" --shell /usr/sbin/nologin tunnel
sudo install -d -m 700 -o tunnel -g tunnel /home/tunnel/.ssh
```

On your laptop, create a dedicated key (do not reuse your own):

```bash
ssh-keygen -t ed25519 -f ./gha-tunnel -C gha-tunnel -N ""
```

Put the **public** key on the server in `/home/tunnel/.ssh/authorized_keys`, as one line with restrictions in front (see `man sshd`, section AUTHORIZED_KEYS FILE FORMAT):

```
restrict,port-forwarding,permitopen="127.0.0.1:5432",command="/bin/false" ssh-ed25519 AAAA... gha-tunnel
```

Permissions: file mode 600, owned by `tunnel`.

Test from your laptop: `ssh -i ./gha-tunnel -N -L 5432:127.0.0.1:5432 tunnel@YOUR_HOST`, then in another terminal connect a Postgres client to `localhost:5432`.

## 6. GitHub secrets (repository settings, Secrets and variables, Actions)

| Secret | Value |
|---|---|
| `VPS_HOST` | server hostname or IP |
| `VPS_TUNNEL_KEY` | contents of the **private** key `gha-tunnel` |
| `VPS_KNOWN_HOSTS` | output of `ssh-keyscan -t ed25519 YOUR_HOST`; verify the fingerprint against your provider's console before saving |
| `DB_OWNER_PASSWORD` | the owner password (migrations only) |
| `DB_INGEST_PASSWORD`, `DB_DBT_PASSWORD`, `DB_READER_PASSWORD` | created with the roles in the first migration (milestone M1) |

Delete `gha-tunnel` from your laptop after saving it, or keep it in your password manager.

Workflow step (pattern; secrets are passed through `env`, not inlined in the script):

```yaml
- name: Open SSH tunnel to Postgres
  env:
    VPS_HOST: ${{ secrets.VPS_HOST }}
    TUNNEL_KEY: ${{ secrets.VPS_TUNNEL_KEY }}
    KNOWN_HOSTS: ${{ secrets.VPS_KNOWN_HOSTS }}
  run: |
    install -m 700 -d ~/.ssh
    printf '%s\n' "$TUNNEL_KEY" > ~/.ssh/tunnel && chmod 600 ~/.ssh/tunnel
    printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts
    ssh -i ~/.ssh/tunnel -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=yes \
        -o ServerAliveInterval=30 -fN -L 5432:127.0.0.1:5432 "tunnel@$VPS_HOST"
```

Jobs then use `postgresql://ingest:...@127.0.0.1:5432/warehouse`. The tunnel encrypts the traffic, so Postgres TLS is not needed on this path.

## 7. Database roles (created by the first migration, M1)

| Role | Can | Used by |
|---|---|---|
| `warehouse_owner` | everything, migrations only | `ingest.yml` migration step, never the app |
| `ingest` | INSERT into `raw` and `meta.run*` | ingesters |
| `dbt` | SELECT `raw`, CREATE/WRITE `stg`, `enrich`, `core`, `mart` | dbt |
| `reader` | SELECT on `core` and `mart` | agents and dashboards |

## 8. Backups (open item for the data engineer, milestone M1b)

A backup that has never been restored does not count. Proposed starting point, not built yet:

- Nightly `pg_dump` (custom format) of `meta` and `core`, encrypted, copied off the server to object storage. Keep 14 daily and 8 weekly.
- A **weekly CI job restores the latest dump** into the throwaway CI Postgres and runs the data-quality tests.
- Provider snapshots as a second layer.
- If point-in-time recovery becomes necessary, evaluate pgBackRest. That is a separate decision.

Tool choice for the dump and upload (candidates: plain `pg_dump` with cron or a systemd timer plus rclone) goes into `docs/decisions/` before it is written.

## 9. Routine care

| Task | How often |
|---|---|
| OS security updates | automatic (unattended-upgrades); reboot when the kernel changes |
| Disk usage | the ingest workflow's size check fails above 70% of the disk |
| Postgres minor updates | `docker compose pull && docker compose up -d` after a fresh dump |
| Postgres major upgrade | dump, restore into a new container, verify, then switch |
| Rotate the tunnel key and DB passwords | yearly, or at once on any suspicion |

## 10. Leaving

`pg_dump` the whole database and restore it into any other Postgres (Neon, Aiven, another VPS). Nothing here uses an extension or feature that locks us in.

## What I could not verify

- The exact current Docker install steps and `sshd` option behaviour on your distribution version. Follow the linked docs if they differ.
- Whether the `nologin` shell together with `command="/bin/false"` and `-N` behaves identically on every sshd version. The test in step 5 confirms it on your server.
- Provider prices and quality.
