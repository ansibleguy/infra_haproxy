<a href="https://www.haproxy.com">
<img src="https://www.haproxy.com/assets/legal/web-logo.png" alt="HAProxy Logo" width="300"/>
</a>

# Ansible Role - HAProxy Community (with ACME, GeoIP and some WAF-Features)

Role to deploy HAProxy (*Focus on the Community Version*)

I think the `frontend` => `route` => `backend` abstraction implemented by this Role is very nice to work with. Please [give me some Feedback](https://github.com/ansibleguy/infra_haproxy/discussions)!

<a href='https://ko-fi.com/ansible0guy' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy me a coffee' />

[![Molecule Test Status](https://badges.ansibleguy.net/infra_haproxy.molecule.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/molecule.sh.j2)
[![YamlLint Test Status](https://badges.ansibleguy.net/infra_haproxy.yamllint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/yamllint.sh.j2)
[![PyLint Test Status](https://badges.ansibleguy.net/infra_haproxy.pylint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/pylint.sh.j2)
[![Ansible-Lint Test Status](https://badges.ansibleguy.net/infra_haproxy.ansiblelint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/ansiblelint.sh.j2)
[![Ansible Galaxy](https://badges.ansibleguy.net/galaxy.badge.svg)](https://galaxy.ansible.com/ui/standalone/roles/ansibleguy/infra_haproxy)

Molecule Logs: [Short](https://badges.ansibleguy.net/log/molecule_infra_haproxy_test_short.log), [Full](https://badges.ansibleguy.net/log/molecule_infra_haproxy_test.log)

**Tested:**
* Debian 12

----

## Install

```bash
# latest
ansible-galaxy role install git+https://github.com/ansibleguy/infra_haproxy

# from galaxy
ansible-galaxy install ansibleguy.infra_haproxy

# or to custom role-path
ansible-galaxy install ansibleguy.infra_haproxy --roles-path ./roles

# install dependencies
ansible-galaxy install -r requirements.yml
```

----

### Roadmap

* Security
  * Basic bot flagging
  * Basic rate limit (GET/HEAD and POST/PUT/DELETE separated)
  * Generic client fingerprint
* 'Interface' for Dict to Map-File translation/creation
* Option to easily Download & Integrate IPLists (*like Tor Exit nodes*)
* Easy way to override the default error-files

----


## Usage

You want a simple Ansible GUI? Check-out my [Ansible WebUI](https://github.com/ansibleguy/webui)

### Examples

Here some detailed config examples and their results:

* [Example ACME](https://github.com/ansibleguy/infra_haproxy/blob/latest/ExampleAcme.md)
* [Example GeoIP](https://github.com/ansibleguy/infra_haproxy/blob/latest/ExampleGeoIP.md)
* [Example WAF](https://github.com/ansibleguy/infra_haproxy/blob/latest/ExampleWAF.md)
* [Example TCP](https://github.com/ansibleguy/infra_haproxy/blob/latest/ExampleTCP.md)

### Config

**Minimal example**

```yaml
haproxy:
  acme:
    enable: true
    email: 'webmaster@template.ansibleguy.net'

  frontends:
    fe_web:
      bind: ['[::]:80 v4v6', '[::]:443 v4v6 ssl']
      acme:
        enable: true

      routes:
        be_intern:
          domains: ['app.template.ansibleguy.net']

      default_backend: 'be_fallback'

  backends:
    be_intern:
      servers:
        - 'srv-1 192.168.10.11:80'
        - 'srv-2 192.168.10.12:80'

    be_fallback:
      lines: 'http-request redirect code 302 location https://github.com/ansibleguy'
```

----

Define the config as needed:

```yaml
haproxy:
  version: '2.8'
  acme:
    enable: true
    email: 'webmaster@template.ansibleguy.net'

  # FRONTENDS
  frontends:
    fe_web:
      bind: ['[::]:80 v4v6', '[::]:443 v4v6 ssl']
      acme:
        enable: true
        domains: ['app.template.ansibleguy.net']  # domains from routes will also be added

      routes:
        be_app01:
          domains: ['app01.template.ansibleguy.net', 'hello.template.ansibleguy.net']

      # define raw config sections/lines to add
      lines:
        section1:
          - ...

      default_backend: 'be_fallback'

    fe_dbs:
      mode: 'tcp'
      default_backend: 'be_db'

    fe_restricted:
      bind: ['[::]:8080 v4v6', '[::]:8443 v4v6 ssl crt /etc/myapp/mycert.pem']

      geoip:
        enable: true

      security:
        restrict_methods: true
        allow_only_methods: ['HEAD', 'GET', 'POST']
        fingerprint_ssl: true  # create and log the JA3 SSL-fingerprint of clients
        
        # very basic filtering of bad bots based on user-agent matching
        block_script_bots: true
        block_bad_crawler_bots: true

      routes:
        be_app02:
          filter_country: ['AT', 'DE', 'CH']
          # filter_ip: ['10.0.0.0/8']
          domains: ['app01.template.ansibleguy.net', 'hello.template.ansibleguy.net']

      # define raw config sections/lines to add
      lines:
        section1:
          - ...

      default_backend: 'be_fallback'

  # BACKENDS
  backends:
    be_app01:
      servers:
        - 'app01-1 10.0.1.1:80'
        - 'app01-2 10.0.1.2:80'

      check_uri: '/health'
      check_expect: 'status 200'

    be_app02:
      security:
        # very basic filtering of bad bots based on user-agent matching
        block_script_bots: true
        block_bad_crawler_bots: true

      ssl: true
      ssl_verify: 'none'  # default; example: 'required ca-file /etc/ssl/certs/my_ca.crt verifyhost host01.intern'
      servers:
        - 'app02-1 10.0.1.1:443'
        - 'app02-2 10.0.1.2:443'

    be_db:
      mode: 'tcp'
      balance: 'roundrobin'
          
      # define raw config sections/lines to add
      lines:
        section1:
          - 'option mysql-check user haproxy_check'

      servers:
        - 'mysql-1 10.0.0.1:3306'
        - 'mysql-2 10.0.0.2:3306'

    be_fallback:
      lines:
        default: 'http-request redirect code 302 location https://github.com/ansibleguy'

  # GENERAL
  stats:
    enable: true  # enable stats http listener
    bind: '127.0.0.1:8404'  # default

  geoip:
    enable: true
    provider: 'ipinfo'  # or 'maxmind'
    token: '<YOUR-TOKEN>'

  # define globals/defaults as key/value pairs (multi-value lists usable)
  global:
    ca-base: '/etc/ssl/certs'

  defaults:
    mode: 'http'
    'timeout connect': 3000
    'timeout server': 5000
    'timeout client': 5000

```

You might want to use 'ansible-vault' to encrypt your passwords:
```bash
ansible-vault encrypt_string
```

----

## Functionality

* **Package installation**
  * Repository dependencies (_minimal_)
  * HAProxy
  * GeoIP
    * [Lookup Service Binary](https://github.com/superstes/geoip-lookup-service)
  * ACME
    * [Dependencies](https://github.com/dehydrated-io/dehydrated/blob/v0.7.1/dehydrated#L261)
    * Nginx light for challenge-response handling


* **Configuration**

  * **Default config**:
    * Globals/Defaults - as seen in default installations


  * **Default opt-ins**:
    * Frontend
      * HTTP mode
        * Redirect non SSL traffic to SSL
        * Logging User-Agent
        * Setting basic security-headers
        * Blocking TRACE & CONNECT methods


  * **Default opt-outs**:
    * Stats http listener
    * Frontend
      * [ACME/LetsEncrypt](https://github.com/dehydrated-io/dehydrated)
      * [GeoIP Lookups](https://github.com/superstes/haproxy-geoip)
      * Blocking of well-known Script-Bots
      * SSL Fingerprinting ([JA3](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967/?ref=waf.ninja))

    * Backend
      * Sticky sessions
      * Blocking TRACE & CONNECT methods

----

## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of the role's functionality can be opted in or out.

  For all available options - see the default-config located in [the main defaults-file](https://github.com/ansibleguy/infra_haproxy/blob/latest/defaults/main/1_main.yml)!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Info:** You can easily filter access to backends by using the `filter` and `filter_not` settings:

    `filter_ip`, `filter_not_ip`, `filter_country`, `filter_not_country`, `filter_asn`, `filter_not_asn`


* **Info:** A very basic user-agent based Script- & Bad-Crawler-Bot blocking can be activated for frontends and backends. Check out the [defaults](https://github.com/ansibleguy/infra_haproxy/blob/latest/defaults/main/2_waf.yml) for the list of bots that are blocked.


* **Info:** You can easily restrict the HTTP methods allowed on a specific frontend or backend by setting `security.restrict_methods` to true and specifying `security.allow_only_methods`


* **Info:** Check out the [Fingerprinting Docs](https://github.com/ansibleguy/infra_haproxy/blob/latest/Fingerprinting.md) for detailed information on how you might want to track clients.


* **Info:** If you are using [Graylog Server](https://graylog.org/products/source-available/) to gather and analyze your logs - make sure to split your HAProxy logs into fields using pipeline rules. Example: [HAProxy Community - Graylog Pipeline Rule](https://gist.github.com/superstes/a2f6c5d855857e1f10dcb51255fe08c6#haproxy-split)



### GeoIP


* **Warning**: If you use the auto-provisioned GeoIP databases - make sure your product follows their license agreement:

    * **IPinfo**: [Information](https://ipinfo.io/products/free-ip-database), [CC4 License](https://creativecommons.org/licenses/by-sa/4.0/) (*allows for commercial usage - you need to add an attribution*)

        **Attribution**: `<p>IP address data powered by <a href="https://ipinfo.io">IPinfo</a></p>`

    * **MaxMind**: [Information](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data), [EULA](https://www.maxmind.com/en/geolite2/eula) (*allows for limited commercial usage - you need to add an attribution*)

        **Attribution**: `This product includes GeoLite2 data created by MaxMind, available from <a href="https://www.maxmind.com">https://www.maxmind.com</a>.`


* **Info**: For GeoIP Tokens you will have to create a free account:

    * **IPInfo**: [Login/Register](https://ipinfo.io/login)
    * **MaxMind**: [Login/Register](https://www.maxmind.com/en/account/login) - Set the `token` to `<ACCOUNT>:<LICENSE>`


* **Info**: If you want to self-manage the GeoIP-databases (*not recommended*) - the role will assume they are placed at `/var/local/lib/geoip` and be named `asn.mmdb` & `country.mmdb`.


* **Info**: You can test the [GeoIP Lookup Microservice](https://github.com/superstes/haproxy-geoip) manually by using curl: `curl 'http://127.0.0.1:10069/?lookup=country&ip=1.1.1.1'`

### WAF

* **Note**: The WAF/security feature-set this role provides does not come lose to the one [available in HAProxy Enterprise by default](https://www.haproxy.com/solutions/web-application-firewall). If you have the money - go for it.

### TCP

* **Info**: If you want to capture data dynamically, you can use `tcp-request content capture`.

    You have to enable the logging of captured data manually by modifying the log-format: `{% raw %}<DEFAULT LOG FORMAT HERE> {%[capture.req.hdr(0)]|%[capture.req.hdr(1)]}{% endraw %}`

    This can be used to log the SNI or GeoIP information.

----

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

There are also some useful **tags** available:
* install
* config => only update config and ssl certs
* ssl or acme
* geoip

To debug errors - you can set the 'debug' variable at runtime:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e debug=yes
```
