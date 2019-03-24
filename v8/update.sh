/home/chenjian/venv/bin/pip uninstall -y v8
rm -rf /home/chenjian/venv/lib/python2.7/site-packages/v8*
/home/chenjian/venv/bin/python setup.py install
sed -i "s|DEBUG = True|DEBUG = False|g" /home/chenjian/venv/lib/python2.7/site-packages/v8*/v8/config/config_dev.py
find /home/chenjian/venv/lib/python2.7/site-packages/v8*/v8/ -name 'config_dev.pyc' -exec rm -f {} \;
