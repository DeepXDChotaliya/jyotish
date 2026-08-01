# Deploying Jyotish.ai

## Read this first

The astronomy comes from **Swiss Ephemeris, which is a Python extension**. It
cannot run in a browser. Uploading `index.html` on its own gives you a form
that looks right and computes nothing — that is exactly the "chart engine is
not reachable" message you saw.

So the host has to run Python. Two ways, both covered below.

| | Hostinger shared / Premium / Business | Hostinger VPS |
|---|---|---|
| How it runs | CGI, one process per request | A long-running server behind nginx |
| Speed | ~1s per chart (Python starts each time) | ~200ms per chart |
| Setup | Upload files, run one pip command | systemd unit plus nginx |
| Needs SSH | Once, to install pyswisseph | Yes |

Start with shared hosting. Move to the VPS if the per-request startup annoys
you.

---

## A. Hostinger shared hosting, in a subfolder

### 1. Build the upload folder

On your Mac, in the project:

    ./deploy/build.sh jyotish

That writes `dist/`. Pass whatever folder name you want, or nothing for the
domain root.

### 2. Upload

Upload the **contents** of `dist/` into `public_html/jyotish/` using hPanel's
File Manager or FTP. You should end up with:

    public_html/jyotish/index.html
    public_html/jyotish/cities.json
    public_html/jyotish/icon.svg
    public_html/jyotish/manifest.webmanifest
    public_html/jyotish/.htaccess
    public_html/jyotish/engine/.htaccess
    public_html/jyotish/engine/deploy/index.cgi
    public_html/jyotish/engine/jyotish/*.py
    public_html/jyotish/engine/ui/*

Two files start with a dot. File Manager hides those by default — turn on
"Show hidden files" or they will silently not upload, and nothing will work.

### 3. Make the CGI script executable

In File Manager, right-click `engine/deploy/index.cgi` → Permissions → **755**.
Over FTP:

    chmod 755 public_html/jyotish/engine/deploy/index.cgi

FTP clients routinely drop the execute bit. If you get a 500 error, check this
first.

### 4. Install the dependencies, once

Enable SSH in hPanel (Advanced → SSH Access), then:

    ssh -p 65002 u123456789@your-server-ip
    pip3 install --user pyswisseph tzdata

`pyswisseph` ships prebuilt Linux wheels, so this normally takes a few seconds
and needs no compiler.

### 5. Check it

Open:

    https://your-domain.com/jyotish/api/diag

That returns a JSON report: Python version, whether Swiss Ephemeris imported,
whether the ayanamsa computes to a sane value, whether the database directory
is writable. If `"ok": true`, you are done — open
`https://your-domain.com/jyotish/` and cast a chart.

If not, `problems` tells you exactly what to fix.

### Troubleshooting

**500 Internal Server Error** — almost always one of three things: `index.cgi`
is not 755; the file has Windows line endings (run `dos2unix index.cgi`); or
`pip3 install --user pyswisseph` was never run. Hostinger's error log is in
hPanel under Advanced → Error Log.

**404 on /api/diag** — `.htaccess` did not upload, or `mod_rewrite` is off.
Confirm the dotfile is there.

**"chart engine is not reachable" still showing** — the page is loading but
`/api/*` is not reaching Python. Open `/jyotish/api/health` directly. HTML back
means the rewrite is not firing; JSON back means the front end is fine and the
browser cached the old page, so hard-refresh.

**Charts are slow** — expected on CGI. Python restarts per request, so the
first chart takes about a second. Move to the VPS setup if it bothers you.

---

## B. Hostinger VPS

    ssh root@your-vps-ip
    apt update && apt install -y python3-venv nginx
    adduser --system --group --home /opt/jyotish jyotish

Upload the project to `/opt/jyotish/app`, then:

    cd /opt/jyotish/app
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m jyotish.places

Install the unit and the site config from this folder:

    cp deploy/jyotish.service /etc/systemd/system/
    systemctl daemon-reload && systemctl enable --now jyotish
    systemctl status jyotish

    cp deploy/nginx.conf.example /etc/nginx/sites-available/jyotish
    ln -s /etc/nginx/sites-available/jyotish /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx

Then TLS:

    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d your-domain.com

---

## Security, plainly

**There is no login.** Anything that can reach the app can read and write every
saved chart, and this is birth data.

On shared hosting the supplied `.htaccess` blocks direct download of the Python
source and the database, but it does not stop anyone using the app itself. If
the charts are not meant to be public, put HTTP basic auth in front of it:

    # in public_html/jyotish/.htaccess
    AuthType Basic
    AuthName "Jyotish"
    AuthUserFile /home/u123456789/.htpasswd
    Require valid-user

Generate the password file with `htpasswd -c ~/.htpasswd yourname` over SSH.

On the VPS, put the same thing in the nginx config, or keep it on a private
network.

The SQLite database lives at `~/.jyotish/practice.db` on whatever account runs
the process. Back it up; it holds the birth records, and charts are
recomputable but the records are not.
