import confluent.config.configmanager as configmanager
import confluent.netutil as netutil
import crypt
import json
import yaml


def yamldump(input):
    return yaml.safe_dump(input, default_flow_style=False)


def handle_request(env, operation, start_response):
    nodename = env.get('HTTP_CONFLUENT_NODENAME', None)
    apikey = env.get('HTTP_CONFLUENT_APIKEY', None)
    if not (nodename and apikey):
        start_response('401 Unauthorized', [])
        yield 'Unauthorized'
        return
    cfg = configmanager.ConfigManager(None)
    eak = cfg.get_node_attributes(nodename, 'api.key').get(
        nodename, {}).get('api.key', {}).get('value', None)
    if not eak:
        start_response('401 Unauthorized', [])
        yield 'Unauthorized'
        return
    salt = '$'.join(eak.split('$', 3)[:-1]) + '$'
    if crypt.crypt(apikey, salt) != eak:
        start_response('401 Unauthorized', [])
        yield 'Unauthorized'
        return
    retype = env.get('HTTP_ACCEPT', 'application/yaml')
    if retype == '*/*':
        retype = 'application/yaml'
    if retype == 'application/yaml':
        dumper = yamldump
    elif retype == 'application/json':
        dumper = json.dumps
    else:
        start_response('406 Not supported', [])
        yield 'Unsupported content type in ACCEPT: ' + retype
        return
    if env['PATH_INFO'] == '/self/deploycfg':
        myip = env.get('HTTP_X_FORWARDED_HOST', None)
        myip = myip.replace('[', '').replace(']', '')
        ncfg = netutil.get_nic_config(cfg, nodename, serverip=myip)
        if ncfg['prefix']:
            ncfg['ipv4_netmask'] = netutil.cidr_to_mask(ncfg['prefix'])
        deployinfo = cfg.get_node_attributes(nodename, 'deployment.*')
        deployinfo = deployinfo.get(nodename, {})
        profile = deployinfo.get(
            'deployment.pendingprofile', {}).get('value', '')
        ncfg['profile'] = profile
        protocol = deployinfo.get('deployment.useinsecureprotocols', {}).get(
            'value', 'never')
        if protocol == 'always':
            ncfg['protocol'] = 'http'
        else:
            ncfg['protocol'] = 'https'
        start_response('200 OK', (('Content-Type', retype),))
        yield dumper(ncfg)
    else:
        start_response('404 Not Found', ())
        yield 'Not found'