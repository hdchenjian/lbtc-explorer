#!/usr/bin/env python3
# encoding: utf-8

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import re
import os

def rpc_doc():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    all_function_str = rpc_connection.help()
    all_function_str = all_function_str.split('\n')

    all_function = []
    supported_commands = ''
    for _function in all_function_str:
        if not _function:
            continue
        if '== ' in _function:
            supported_commands += ('<li style="list-style-type: none;"><p style="font-weight:bold; margin-top: 10px;margin-bottom: 0px;">%s</p></li>\n' % _function.strip(' ='))
            continue
        #print(_function)
        if ' ' not in _function:
            _function_name = _function
        else:
            _function_name = _function.split(' ')[0]
        all_function.append(_function_name)
        
        supported_commands += ('<li><a href="/lbtc/rpc?cmd=%s">%s</a></li>\n' % (_function_name, _function_name))
        #print(all_function)
    html_header = '''{% extends "rpc/base.html" %}
    {% block body %}
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <h3>A web based interface to the LBTC API JSON-RPC</h3>
          </div>
          <div class="col-md-9">
            <br/>
            <h4>Command: '''
    html_command ='''
            <label class="control-label">RPC Help</label>
            <pre>'''
    html_content = '''
            </pre>
          </div>
    
          <div class="col-md-3">
            <p>Supported Commands:</p>
            <ul>
        '''
    
    html_end = '''
            </ul>
          </div>
        </div>
      </div>
    {% endblock %}
    '''

    supported_commands_file_name = '/tmp/supported_commands_file.html'
    if os.path.isfile(supported_commands_file_name):
        supported_commands_file = open(supported_commands_file_name, 'rU')
        supported_commands = supported_commands_file.read()
        supported_commands_file.close()
        print(supported_commands)
    else:
        supported_commands_file = open(supported_commands_file_name, 'w')
        supported_commands_file.write(supported_commands)
        supported_commands_file.close()

    for _function in all_function:
        doc_file = open('templates/rpc/' + _function + '.html', 'w')
        cmd_help = rpc_connection.help(_function)
        api_form_start = '''
        <form method="GET" action="/lbtc/rpc">
          <div class="form-group">
            <input id='run' type="hidden" name="run" value="1" />
            <input id='param0' type="hidden" name="cmd" value="%s" />
          </div>
        ''' % _function
        api_params = ''
        no_parameter = True
        if cmd_help.find('Arguments:') > 0:
            no_parameter = False
            index = 1
            cmd_params = cmd_help[cmd_help.find('Arguments:') + len('Arguments:') : cmd_help.find('Result')]
            cmd_params = cmd_params.split('\n')
            #print(cmd_help.find('Arguments:'), _function, cmd_params, cmd_help)
            for _param in cmd_params:
                if not _param:
                    continue
                if not re.match('[0-9]\. ', _param):
                    continue
                param_hint = _param.split('. ')
                placeholder = param_hint[1].split(' ')[0]
                placeholder = placeholder.strip('"')
                param_type = param_hint[1]
                if 'required' in param_type[param_type.find(' (') : param_type.find(') ')]:
                    required = 'required'
                else:
                    required = ''
                param_name = 'param' + str(index)
                api_params += '''
                <div class="form-group">
                  <input size=55 id="''' + param_name + '" name="' + param_name + '" value="" placeholder="' + placeholder + '" ' + required + '''/>
                </div>
                '''
                index += 1
        else:
            api_params = ''
        api_form_end = '''
            <button class="btn btn-primary" id="current_page_next_button" >Execute Command</button>
            <br/><br/><br/>
        </form>
        '''
        command_result = '''
        {% if result != 'default_string_doc' %}
        <label class="control-label">Command Result</label>
        <pre>{{ result }}</pre>
        <br/><br/><br/>
        {% endif %}
        '''
        if no_parameter:
            command_parameter = '</h4><br/><h4>Command parameter: no parameter</h4>'
        else:
            command_parameter = '</h4><br/><h4>Command parameter:</h4>'
        html_param_notice = ''
        if _function == 'createrawtransaction':
            print(_function)
            html_param_notice = '''
    <pre>
1. inputs: A json array, such as:
[{"txid": "cb379239b191e9eb348da32c7d4eab36a4ab6ec613f6eafb280b083ff4f99389", "vout": 0},
 {"txid": "fcd5fd6941d1c1c5bf1bd2f8d4c025443a56303140a2266b0d3eddcb3e40e9f6", "vout": 0}]

2. outputs: A json object, such as
{"166D9UoFdPcDEGFngswE226zigS8uBnm3C": 0.01, "1FF3GjBcybbBTmTnC4DFSRGKJjBP1art2c": 0.01}

this will send the two address 0.01 LBTC each

Result is the hex string of the transaction.
You can use <a href="/lbtc/rpc?cmd=decoderawtransaction">decoderawtransaction</a> command to decode the hex-encoded transaction.
    </pre>
            '''
        doc_file.write(html_header + _function + command_parameter + api_form_start + api_params + api_form_end +
                       command_result + html_param_notice + html_command + cmd_help.replace('<', '&lt').replace('>', '&gt') + html_content)
        doc_file.write(supported_commands)
        doc_file.write(html_end)
        doc_file.close()
        #break
    print('command number: ', len(all_function))


if __name__ == '__main__':
    rpc_doc()
