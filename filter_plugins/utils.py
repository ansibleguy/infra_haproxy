from re import sub as regex_replace


class FilterModule(object):

    def filters(self):
        return {
            "ensure_list": self.ensure_list,
            "is_string": self.is_string,
            "is_dict": self.is_dict,
            "safe_key": self.safe_key,
            "ssl_fingerprint_active": self.ssl_fingerprint_active,
            "build_route": self.build_route,
        }

    @staticmethod
    def ensure_list(data: (str, list)) -> list:
        # if user supplied a string instead of a list => convert it to match our expectations
        if isinstance(data, list):
            return data

        return [data]

    @staticmethod
    def is_string(data) -> bool:
        return isinstance(data, str)

    @staticmethod
    def is_dict(data) -> bool:
        return isinstance(data, dict)

    @staticmethod
    def safe_key(key: str) -> str:
        return regex_replace('[^0-9a-zA-Z_]+', '', key.replace(' ', '_'))

    @staticmethod
    def ssl_fingerprint_active(frontends: dict) -> bool:
        for fe_cnf in frontends.values():
            try:
                if fe_cnf['security']['fingerprint_ssl']:
                    return True

            except KeyError:
                continue

        return False

    @staticmethod
    def is_truthy(v: (bool, str, int)) -> bool:
        return v in [True, 'yes', 'y', 'Yes', 'YES', 'true', 1, '1']

    @classmethod
    def build_route(cls, fe_cnf: dict, be_cnf: dict, be_name: str) -> list:
        lines = []
        to_match = []
        var_prefix = f'{be_name}_filter'

        if fe_cnf['mode'] == 'http' and len(be_cnf['domains']) > 0:
            lines.append(
                f"acl {var_prefix}_domains req.hdr(host) "
                f"-m str -i {' '.join(cls.ensure_list(be_cnf['domains']))}"
            )
            to_match.append(f'{var_prefix}_domains')

        if len(be_cnf['filter_ip']) > 0:
            lines.append(f"acl {var_prefix}_ip src {' '.join(cls.ensure_list(be_cnf['filter_ip']))}")
            to_match.append(f'{var_prefix}_ip')

        if len(be_cnf['filter_not_ip']) > 0:
            lines.append(f"acl {var_prefix}_not_ip src {' '.join(cls.ensure_list(be_cnf['filter_not_ip']))}")
            to_match.append(f'!{var_prefix}_not_ip')

        if cls.is_truthy(fe_cnf['geoip']['enable']):
            if cls.is_truthy(fe_cnf['geoip']['country']):
                if len(be_cnf['filter_country']) > 0:
                    lines.append(
                        f"acl {var_prefix}_country var(txn.geoip_country) "
                        f"-m str -i {' '.join(cls.ensure_list(be_cnf['filter_country']))}"
                    )
                    to_match.append(f'{var_prefix}_country')

                if len(be_cnf['filter_not_country']) > 0:
                    lines.append(
                        f"acl {var_prefix}_not_country var(txn.geoip_country) "
                        f"-m str -i {' '.join(cls.ensure_list(be_cnf['filter_not_country']))}"
                    )
                    to_match.append(f'!{var_prefix}_not_country')

            if cls.is_truthy(fe_cnf['geoip']['asn']):
                if len(be_cnf['filter_asn']) > 0:
                    lines.append(
                        f"acl {var_prefix}_asn var(txn.geoip_asn) "
                        f"-m str -i {' '.join(cls.ensure_list(be_cnf['filter_asn']))}"
                    )
                    to_match.append(f'{var_prefix}_asn')

                if len(be_cnf['filter_not_asn']) > 0:
                    lines.append(
                        f"acl {var_prefix}_not_asn var(txn.geoip_asn) "
                        f"-m str -i {' '.join(cls.ensure_list(be_cnf['filter_not_asn']))}"
                    )
                    to_match.append(f'!{var_prefix}_not_asn')

        if len(to_match) > 0:
            lines.append(f"use_backend {be_name} if {' '.join(to_match)}")

        else:
            lines.append(f"use_backend {be_name}")

        return lines
