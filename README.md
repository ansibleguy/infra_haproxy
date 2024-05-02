<a href="https://www.haproxy.com">
<img src="https://www.haproxy.com/assets/legal/web-logo.png" alt="HAProxy Logo" width="300"/>
</a>

# Ansible Role - HAProxy Community

**WARNING**: The role is still in early development! **DO NOT TRY TO USE IN PRODUCTION**!

Role to deploy HAProxy (*Focus on the Community Version*)

<a href='https://ko-fi.com/ansible0guy' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy me a coffee' />

[![Molecule Test Status](https://badges.ansibleguy.net/infra_haproxy.molecule.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/molecule.sh.j2)
[![YamlLint Test Status](https://badges.ansibleguy.net/infra_haproxy.yamllint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/yamllint.sh.j2)
[![PyLint Test Status](https://badges.ansibleguy.net/infra_haproxy.pylint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/pylint.sh.j2)
[![Ansible-Lint Test Status](https://badges.ansibleguy.net/infra_haproxy.ansiblelint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/ansiblelint.sh.j2)
[![Ansible Galaxy](https://badges.ansibleguy.net/galaxy.badge.svg)](https://galaxy.ansible.com/ui/standalone/roles/ansibleguy/infra_haproxy)

Molecule Logs: [Short](https://badges.ansibleguy.net/log/molecule_infra_haproxy_test_short.log), [Full](https://badges.ansibleguy.net/log/molecule_infra_haproxy_test.log)

**Tested:**
* Debian 12

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

## Functionality

* **Package installation**
  * Repository dependencies (_minimal_)
  * HAProxy


* **Configuration**

  * **Default config**:
    * Globals/Defaults - as seen in default installations
    * Backend
      * Balance mode 'leastconn'
      * Server SSL
      * Server SSL verification
      * Health-Check
 

  * **Default opt-ins**:
    * Frontend
      * Redirect non SSL traffic to SSL if in HTTP mode
      * Logging User-Agent
      * Setting basic security-headers
    * Backend
      * Basic Check (*httpchk if in http mode*)


  * **Default opt-outs**:
    * Stats http listener
    * Frontend
      * [ACME/LetsEncrypt](https://www.haproxy.com/blog/haproxy-and-let-s-encrypt) (*yet to be implemented*)
      * [GeoIP Lookups](https://github.com/superstes/haproxy-geoip)


## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of the role's functionality can be opted in or out.

  For all available options - see the default-config located in the main defaults-file!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Warning:** If you use the auto-provisioned GeoIP databases - make sure your product follows their license agreement:

    * **IPinfo**: [Information](https://ipinfo.io/products/free-ip-database), [CC4 License](https://creativecommons.org/licenses/by-sa/4.0/) (*allows for commercial usage - you need to add an attribution*)

        **Attribution**: `<p>IP address data powered by <a href="https://ipinfo.io">IPinfo</a></p>`

    * **MaxMind**: [Information](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data), [EULA](https://www.maxmind.com/en/geolite2/eula) (*allows for limited commercial usage - you need to add an attribution*)

        **Attribution**: `This product includes GeoLite2 data created by MaxMind, available from <a href="https://www.maxmind.com">https://www.maxmind.com</a>.`


* **Info**: If you want to self-manage the databases - the role will assume they are placed at `/var/local/lib/geoip` and be named `asn.mmdb` & `country.mmdb`.


* **Info**: For GeoIP Tokens you will have to create a free account:

    * **IPInfo**: [Login/Register](https://ipinfo.io/login)
    * **MaxMind**: [Login/Register](https://www.maxmind.com/en/account/login) - Set the `token` to `<ACCOUNT>:<LICENSE>`


* **Info**: You can test the [GeoIP Lookup Microservice](https://github.com/superstes/haproxy-geoip) manually by using curl: `curl 'http://127.0.0.1:10069/?lookup=country&ip=1.1.1.1'`


* **Info**: You can easily filter access to backends by using the `filter` and `filter_not` settings:

    `filter_ip`, `filter_not_ip`, `filter_country`, `filter_not_country`, `filter_asn`, `filter_not_asn`


## Usage

### Config

**Minimal example**

```yaml
haproxy:
  frontends:
    fe_web:
      bind: ['[::]:80 v4v6', '[::]:443 v4v6 ssl']
      acme: true
      acme_domains: ['app.template.ansibleguy.net']
      
      route:
        be_intern:
          filter_ip: '10.0.0.0/8'
          filter_not_ip: '10.100.0.0/24'

      default_backend: 'be_fallback'

  backends:
    be_intern:
      

    be_fallback:
      lines: 'http-request redirect code 301 location https://github.com/ansibleguy'
```

Define the config as needed:

```yaml
haproxy:
  version: '2.8'

  # FRONTENDS
  frontends:
    fe_web:
      bind: ['[::]:80 v4v6', '[::]:443 v4v6 ssl']
      acme: true
      acme_domains: ['app.template.ansibleguy.net']  # domains from routes will also be added

      route:
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
      bind: ['[::]:80 v4v6', '[::]:443 v4v6 ssl']
      acme: true

      geoip:
        enable: true

      backends:
        be_app01:
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
        default: 'http-request redirect code 301 location https://github.com/ansibleguy'

  # GENERAL
  stats:  # enable stats http page
    http: true
    bind: '127.0.0.1:8404'

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

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

There are also some useful **tags** available:
* install
* config
* ssl
* geoip

To debug errors - you can set the 'debug' variable at runtime:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e debug=yes
```
