# Basic Example with GeoIP

## Config

```yaml
haproxy:
  geoip:
    enable: true
    token: "<YOUR TOKEN>"

  frontends:
    fe_web:
      bind: ['[::]:80 v4v6']
      geoip:
        enable: true
        country: true
        asn: true

      routes:
        be_test1:
          domains: ['app1.test.ansibleguy.net']
          filter_country: 'AT'
          filter_asn: '1337'

        be_test2:
          domains: ['app2.test.ansibleguy.net']
          filter_not_country: ['CN', 'RU', 'US']
          filter_not_asn: ['100000', '120000']

      default_backend: 'be_fallback'

  backends:
    be_test1:
      servers: 'srv1 192.168.10.11:80'

    be_test2:
      servers: 'srv2 192.168.10.12:80'

    be_fallback:
      lines: 'http-request redirect code 301 location https://github.com/ansibleguy'
```

----

## Result

```bash
root@test-ag-haproxy-acme:/# cat /etc/haproxy/haproxy.cfg 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_haproxy
> 
> global
>     daemon
>     user haproxy
>     group haproxy
> 
> 
>     log /dev/log    local0
>     log /dev/log    local1 notice
>     chroot /var/lib/haproxy
>     stats socket /run/haproxy/admin.sock mode 660 level admin
>     stats timeout 30s
>     ca-base /etc/ssl/certs
>     crt-base /etc/ssl/private
>     ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
>     ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
>     ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
>     tune.ssl.capture-buffer-size 96

> defaults
>     log global
>     mode http
>     option httplog
>     option dontlognull
>     timeout connect 5000
>     timeout client 50000
>     timeout server 50000
>     errorfile 400 /etc/haproxy/errors/400.http
>     errorfile 403 /etc/haproxy/errors/403.http
>     errorfile 408 /etc/haproxy/errors/408.http
>     errorfile 500 /etc/haproxy/errors/500.http
>     errorfile 502 /etc/haproxy/errors/502.http
>     errorfile 503 /etc/haproxy/errors/503.http
>     errorfile 504 /etc/haproxy/errors/504.http

root@test-ag-haproxy-geoip:/# cat /etc/haproxy/conf.d/frontend.cfg 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_haproxy
> 
> frontend fe_web
>     mode http
>     bind [::]:80 v4v6
> 
>     # GEOIP
>     acl private_nets src 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.0/8 ::1
>     http-request set-var(txn.geoip_country) str(00) if private_nets
> 
>     ## GEOIP COUNTRY
>     acl geoip_country_in_map src,ipmask(24,48),map_ip(/etc/haproxy/map/geoip_country.map) -m found
>     http-request set-var(txn.geoip_country) src,ipmask(24,48),map(/etc/haproxy/map/geoip_country.map) if !private_nets geoip_country_in_map
>     http-request lua.lookup_geoip_country if !{ var(txn.geoip_country) -m found }
>     http-request set-map(/etc/haproxy/map/geoip_country.map) %[src,ipmask(24,48)] %[var(txn.geoip_country)] if !private_nets !geoip_country_in_map
>     http-request capture var(txn.geoip_country) len 2
> 
>     ## GEOIP ASN
>     acl geoip_asn_in_map src,ipmask(24,48),map_ip(/etc/haproxy/map/geoip_asn.map) -m found
>     http-request set-var(txn.geoip_asn) src,ipmask(24,48),map(/etc/haproxy/map/geoip_asn.map) if !private_nets geoip_asn_in_map
>     http-request lua.lookup_geoip_asn if !{ var(txn.geoip_asn) -m found }
>     http-request set-map(/etc/haproxy/map/geoip_asn.map) %[src,ipmask(24,48)] %[var(txn.geoip_asn)] if !private_nets !geoip_asn_in_map
>     http-request capture var(txn.geoip_asn) len 10
> 
>     # Security headers
>     http-response set-header Strict-Transport-Security "max-age=16000000; includeSubDomains; preload;"
>     http-response set-header X-Frame-Options "DENY"
>     http-response set-header X-Content-Type-Options "nosniff"
>     http-response set-header X-Permitted-Cross-Domain-Policies "none"
>     http-response set-header X-XSS-Protection "1; mode=block"
> 
>     http-request capture req.fhdr(User-Agent) len 200
> 
>     # BACKEND be_test1
>     acl be_test1_domains req.hdr(host) -m str -i app1.test.ansibleguy.net    acl be_test1_filter_ip always_true
>     acl be_test1_filter_not_ip always_false
>     acl be_test1_filter_country var(txn.geoip_country) -m str -i AT
>     acl be_test1_filter_not_country always_false
>     acl be_test1_filter_asn var(txn.geoip_asn) -m int -i 1337
>     acl be_test1_filter_not_asn always_false
> 
>     use_backend be_test1 if be_test1_domains be_test1_filter_ip !be_test1_filter_not_ip be_test1_filter_asn !be_test1_filter_not_asn be_test1_filter_country !be_test1_filter_not_country
> 
>     # BACKEND be_test2
>     acl be_test2_domains req.hdr(host) -m str -i app2.test.ansibleguy.net
>     acl be_test2_filter_ip always_true
>     acl be_test2_filter_not_ip always_false
>     acl be_test2_filter_country always_true
>     acl be_test2_filter_not_country var(txn.geoip_country) -m str -i CN RU US
>     acl be_test2_filter_asn always_true
>     acl be_test2_filter_not_asn var(txn.geoip_asn) -m int -i 100000 120000
> 
>     use_backend be_test2 if be_test2_domains be_test2_filter_ip !be_test2_filter_not_ip be_test2_filter_asn !be_test2_filter_not_asn be_test2_filter_country !be_test2_filter_not_country
> 
>     default_backend be_fallback

root@test-ag-haproxy-geoip:/# cat /etc/haproxy/conf.d/backend.cfg 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_haproxy
> 
> 
> backend be_test1
>     mode http
>     balance leastconn
> 
>     server srv1 192.168.10.11:80 check
>
> 
> backend be_test2
>     mode http
>     balance leastconn
> 
>     server srv2 192.168.10.12:80 check
> 
> backend be_fallback
>     mode http
>     balance leastconn
> 
>     # SECTION: default
>     http-request redirect code 301 location https://github.com/ansibleguy
> 
> backend be_haproxy_geoip
>     server haproxy_geoip 127.0.0.1:8406 check

root@test-ag-haproxy-geoip:/# systemctl status haproxy.service
> * haproxy.service - HAProxy Load Balancer
>      Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; preset: enabled)
>     Drop-In: /etc/systemd/system/haproxy.service.d
>              `-override.conf
>      Active: active (running) since Sat 2024-05-04 16:56:45 UTC; 5s ago
>        Docs: man:haproxy(1)
>              file:/usr/share/doc/haproxy/configuration.txt.gz
>              https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/
>              https://github.com/ansibleguy/infra_haproxy
>     Process: 3364 ExecStartPre=/usr/sbin/haproxy -c -f $CONFIG -f /etc/haproxy/conf.d/ (code=exited, status=0/SUCCESS)
>    Main PID: 3366 (haproxy)
>      Status: "Ready."
>       Tasks: 7 (limit: 1783)
>      Memory: 122.2M
>         CPU: 109ms
>      CGroup: /system.slice/haproxy.service
>              |-3366 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/ -p /run/haproxy.pid -S /run/haproxy-master.sock
>              `-3368 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/ -p /run/haproxy.pid -S /run/haproxy-master.sock

root@test-ag-haproxy-geoip:/# systemctl status haproxy-geoip-lookup.service
> * haproxy-geoip-lookup.service - HAProxy GeoIP Lookup Service
>      Loaded: loaded (/etc/systemd/system/haproxy-geoip-lookup.service; enabled; preset: enabled)
>      Active: active (running) since Sat 2024-05-04 16:45:33 UTC; 8min ago
>        Docs: https://github.com/superstes/geoip-lookup-service
>              https://github.com/ansibleguy/infra_haproxy
>    Main PID: 2917 (geoip-lookup)
>       Tasks: 5 (limit: 1783)
>      Memory: 2.4M
>         CPU: 2ms
>      CGroup: /system.slice/haproxy-geoip-lookup.service
>              `-2917 /usr/local/bin/geoip-lookup -l 127.0.0.1 -p 8406 -t ipinfo -plain -country /var/local/lib/geoip/country.mmdb -asn /var/local/lib/geoip/asn.mmdb

root@test-ag-haproxy-geoip:/# systemctl status haproxy-geoip-update.service
> * haproxy-geoip-update.service - HAProxy GeoIP Update Service
>      Loaded: loaded (/etc/systemd/system/haproxy-geoip-update.service; disabled; preset: enabled)
>      Active: inactive (dead)
> TriggeredBy: * haproxy-geoip-update.timer
>        Docs: https://github.com/ansibleguy/infra_haproxy

root@test-ag-haproxy-geoip:/# systemctl status haproxy-geoip-update.timer
> * haproxy-geoip-update.timer - Timer to start HAProxy GeoIP Update
>      Loaded: loaded (/etc/systemd/system/haproxy-geoip-update.timer; enabled; preset: enabled)
>      Active: active (waiting) since Sat 2024-05-04 16:45:29 UTC; 9min ago
>     Trigger: Mon 2024-05-06 01:00:00 UTC; 1 day 8h left
>    Triggers: * haproxy-geoip-update.service
```
