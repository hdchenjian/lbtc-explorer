#!/usr/bin/python
# -*- coding: utf-8 -*-

import contextlib
import datetime

from sqlalchemy.sql import func

from v8.engine import db_conn
from v8.model.device_update import DeviceInfo, FirmInfo, AlgorithmInfo, \
    FpgaInfo, UpdateRule, FpgaVersionMap, DeviceType
from v8.model.user import User
from v8.engine.util import model_to_dict


def get_latest_firm_info(device_type=0, version=''):
    """Get latest update info.

    Args:

    Returns:
        dict of latest update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        filters = [FirmInfo.deleted == 0, FirmInfo.online == 1,
                   FirmInfo.device_type == device_type]
        if version:
            filters.append(FirmInfo.firm_version == version)
        _update_info = session.query(FirmInfo) \
                              .filter(*filters) \
                              .order_by(FirmInfo.firm_version.desc()).first()
        if not _update_info:
            return None
        else:
            return model_to_dict(_update_info)


def get_latest_alg_info(device_type, version=''):
    """Get latest update info.

    Args:

    Returns:
        dict of latest update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        filters = [AlgorithmInfo.deleted == 0, AlgorithmInfo.online == 1,
                   AlgorithmInfo.device_type == device_type]
        if version:
            filters.append(AlgorithmInfo.alg_version == version)
        _update_info = session.query(AlgorithmInfo) \
                              .filter(*filters) \
                              .order_by(
                                  AlgorithmInfo.alg_version.desc()).first()
        if not _update_info:
            return None
        else:
            return model_to_dict(_update_info)


def upload_firm_info(firm_version, firm_url, device_type, md5):
    """Upload firm info.

    Args:
        firm_version (string): firm version.
        firm_url (string) : download file path.

    Returns:
        dict of firm info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _firm_info = session.query(FirmInfo) \
                            .filter(FirmInfo.firm_version == firm_version,
                                    FirmInfo.device_type == device_type) \
                            .first()
        if _firm_info is None:
            _firm_info = FirmInfo()
            _firm_info.create_time = datetime.datetime.now()
        _firm_info.device_type = device_type
        _firm_info.firm_version = firm_version
        _firm_info.firm_url = firm_url
        _firm_info.online = 1
        _firm_info.deleted = 0
        _firm_info.md5 = md5
        _firm_info.update_time = datetime.datetime.now()
        session.add(_firm_info)
        session.commit()
        return model_to_dict(_firm_info)


def upload_alg_info(alg_version, alg_url, device_type, md5):
    """Upload alg info.

    Args:
        alg_version (string): alg version.
        alg_url (string) : download file path.

    Returns:
        dict of alg info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _alg_info = session.query(AlgorithmInfo) \
                           .filter(AlgorithmInfo.alg_version == alg_version,
                                   AlgorithmInfo.device_type == device_type) \
                           .first()
        if _alg_info is None:
            _alg_info = AlgorithmInfo()
            _alg_info.create_time = datetime.datetime.now()
        _alg_info.device_type = device_type
        _alg_info.alg_version = alg_version
        _alg_info.alg_url = alg_url
        _alg_info.online = 1
        _alg_info.deleted = 0
        _alg_info.md5 = md5
        _alg_info.update_time = datetime.datetime.now()
        session.add(_alg_info)
        session.commit()
        return model_to_dict(_alg_info)


def get_all_latest_firm_info(device_type):
    """Get all latest firm info.

    Args:

    Returns:
        dict of latest firm info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        version_to_firm_info = {}
        for _firm_info in session.query(FirmInfo) \
                                 .filter(FirmInfo.deleted == 0,
                                         FirmInfo.device_type == device_type) \
                                 .order_by(FirmInfo.firm_version.desc()):
            firm_info = model_to_dict(_firm_info)
            firm_info['device_num'] = 0
            firm_info['target_device_num'] = 0
            version_to_firm_info[firm_info['firm_version']] = firm_info
            ret.append(firm_info)
        for _version, _count in session \
                .query(DeviceInfo.firm_version,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.firm_version):
            if _version in version_to_firm_info:
                version_to_firm_info[_version]['device_num'] = _count
        for _version, _count in session \
                .query(DeviceInfo.firm_version_target,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.firm_version_target):
            if _version in version_to_firm_info:
                version_to_firm_info[_version]['target_device_num'] = _count
        return ret


def online_firm_info_with_firm_version(firm_version, device_type):
    """Online update info.

    Args:
        firm_version (string): firm version

    Returns:
        dict of update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(FirmInfo) \
                              .filter(
                                  FirmInfo.deleted == 0,
                                  FirmInfo.online == 0,
                                  FirmInfo.device_type == device_type,
                                  FirmInfo.firm_version == firm_version) \
                              .first()
        if _update_info is None:
            return None
        else:
            _update_info.online = 1
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_update_info)


def offline_firm_info_with_firm_version(firm_version, device_type):
    """Delete update info.

    Args:
        firm_version (string): firm version

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(FirmInfo) \
                              .filter(
                                  FirmInfo.deleted == 0,
                                  FirmInfo.online == 1,
                                  FirmInfo.device_type == device_type,
                                  FirmInfo.firm_version == firm_version) \
                              .first()
        if _update_info is None:
            return False
        else:
            _update_info.online = 0
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return True


def save_device_info(
        device_id, firm_version, alg_version, p2p, device_type, fpga_version):
    """Save device info.

    Args:
        device_id (string): device id
        firm_version (string): firm version
        alg_version (string): alg version
        p2p (int): p2p

    Returns:
        dict of latest update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.device_type == device_type) \
                              .first()
        if not _device_info:
            _device_info = DeviceInfo()
            _device_info.device_id = device_id
            _device_info.device_type = device_type
            _device_info.create_time = datetime.datetime.now()
            _device_info.fpga_version_target = ''
            _device_info.fpga_version_use_confirm = 0
            _device_info.alg_version_target = ''
            _device_info.alg_version_use_confirm = 0
            _device_info.firm_version_target = ''
            _device_info.firm_version_use_confirm = 0
        _device_info.alg_version = alg_version
        _device_info.firm_version = firm_version
        _device_info.fpga_version = fpga_version
        _device_info.p2p = p2p
        _device_info.deleted = 0
        _device_info.update_time = datetime.datetime.now()
        if _device_info.alg_version_target <= _device_info.alg_version:
            _device_info.alg_version_target = ''
        if _device_info.firm_version_target <= _device_info.firm_version:
            _device_info.firm_version_target = ''
        if _device_info.fpga_version_target <= _device_info.fpga_version:
            _device_info.fpga_version_target = ''
        session.add(_device_info)
        session.commit()
        return model_to_dict(_device_info)


def update_device_alg_version(device_id, device_type, use_confirm):
    """Update device algorithm.

    Args:
        device_id (string): device id

    Returns:
        dict of device info or None.
    """
    latest_alg_info = get_latest_alg_info(device_type)
    if latest_alg_info is None:
        return None
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.device_type == device_type,
                                      DeviceInfo.deleted == 0) \
                              .first()
        if _device_info is None:
            return None
        else:
            _device_info.alg_version_target = latest_alg_info['alg_version']
            _device_info.alg_version_use_confirm = use_confirm
            _device_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_device_info)


def update_device_firm_version(device_id, device_type, use_confirm):
    """Update device firm.

    Args:
        device_id (string): device id

    Returns:
        dict of device info or None.
    """
    latest_firm_info = get_latest_firm_info(device_type)
    if latest_firm_info is None:
        return None
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.device_type == device_type,
                                      DeviceInfo.deleted == 0) \
                              .first()
        if _device_info is None:
            return None
        else:
            _device_info.firm_version_target = \
                latest_firm_info['firm_version']
            _device_info.firm_version_use_confirm = use_confirm
            _device_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_device_info)


def update_device_version_target(device_id, version, update_type, use_confirm):
    """Update device firm or alg.

    Args:
        device_id (string): device id
        version (string)
        update_type (int): 0: firm, 1: alg

    Returns:
        dict of device info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if update_type == 0:
            _update_info = session.query(FirmInfo) \
                                  .filter(FirmInfo.deleted == 0,
                                          FirmInfo.online == 1,
                                          FirmInfo.firm_version == version) \
                            .first()
            if _update_info is None:
                return u'固件版本不存在'
        elif update_type == 1:
            _update_info = session.query(AlgorithmInfo) \
                            .filter(AlgorithmInfo.deleted == 0,
                                    AlgorithmInfo.online == 1,
                                    AlgorithmInfo.alg_version == version) \
                            .first()
            if _update_info is None:
                return u'固件版本不存在'
        else:
            _update_info = session.query(FpgaInfo) \
                            .filter(FpgaInfo.deleted == 0,
                                    FpgaInfo.online == 1,
                                    FpgaInfo.fpga_version == version) \
                            .first()
            if _update_info is None:
                return u'固件版本不存在'
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.deleted == 0) \
                              .first()
        if _device_info is None:
            return u'设备不存在'
        if update_type == 0 and _device_info.firm_version < version:
            _device_info.firm_version_target = version
            _device_info.firm_version_use_confirm = use_confirm
        elif update_type == 1 and _device_info.alg_version < version:
            _device_info.alg_version_target = version
            _device_info.alg_version_use_confirm = use_confirm
        elif update_type == 1 and _device_info.fpga_version < version:
            _device_info.fpga_version_target = version
            _device_info.fpga_version_use_confirm = use_confirm
        else:
            return u'升级版本号必须大于设备本身版本号'
        _device_info.update_time = datetime.datetime.now()
        session.commit()
        return u'升级成功'


def cancel_update_device(device_id, cancel_type):
    """cancel update device.

    Args:
        device_id (string): device id
        cancel_type (in): 0: firm 1: algorithm

    Returns:
        dict of device info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.deleted == 0) \
                              .first()
        if _device_info is None:
            return None
        else:
            if cancel_type == 0:
                _device_info.firm_version_target = ''
            elif cancel_type == 1:
                _device_info.alg_version_target = ''
            else:
                _device_info.fpga_version_target = ''
            _device_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_device_info)


def get_device_info(since_id, page_num, device_type):
    """Get device info.

    Args:
        since_id (int): the maximum id of database index(default 0)
        page_num (int): the number of devices of per page

    Returns:
        list of device info.
    """

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        filters = [DeviceInfo.deleted == 0,
                   DeviceInfo.device_type == device_type]
        if since_id > 0:
            filters.append(DeviceInfo.id < since_id)
        _devices = session.query(DeviceInfo) \
                          .filter(*filters) \
                          .order_by(DeviceInfo.id.desc()) \
                          .limit(page_num)
        ret = []
        for _device in _devices:
            ret.append(model_to_dict(_device))
        return ret


def get_device_count(device_type):
    """Get total device number.

    Args:

    Returns:
        the total number of device.
    """

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        device_num = session.query(func.count(DeviceInfo.id)) \
                          .filter(DeviceInfo.deleted == 0,
                                  DeviceInfo.device_type == device_type) \
                          .scalar()
        return device_num


def get_max_id_with_page(current_page, device_per_page, device_type):
    '''Get the maximum index with current page.

    Args:
        current_page(int): current page.
        device_per_page(int): device per page
    Returns:
        the maximum index of device.
    '''

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device = session.query(DeviceInfo) \
                  .filter(DeviceInfo.deleted == 0,
                          DeviceInfo.device_type == device_type,) \
                  .order_by(DeviceInfo.id.desc()) \
                  .offset((current_page - 1) * device_per_page - 1) \
                  .first()
        return _device.id


def search_device_with_device_id(device_id, device_type):
    """Search device which device_id.

    Args:
        device_id (string): device id

    Returns:
        list of device info.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _device_info in session.query(DeviceInfo) \
                .filter(DeviceInfo.device_id.like('%%%s%%' % device_id),
                        DeviceInfo.device_type == device_type,
                        DeviceInfo.deleted == 0):
            ret.append(model_to_dict(_device_info))
        return ret


def update_device_firm_percent_with_firm_version(
        percent, firm_version, device_type, low_firm_version,
        create_update_rule, use_confirm):
    """Update device firm version.

    Args:
        percent (int): the percentage of all device that will be update.
        firm_version (string): firm version.
        low_firm_version (list): only update the version in the list.
        create_update_rule (boolean): True: create update rule

    Returns:
        True when update success whether False.
    """

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if create_update_rule:
            for low_version in low_firm_version:
                update_or_create_update_rule(
                    low_version, firm_version, 0, device_type, use_confirm)
        device_num = session.query(func.count(DeviceInfo.id)).filter(
            DeviceInfo.deleted == 0,
            DeviceInfo.device_type == device_type,
            DeviceInfo.firm_version < firm_version,
            DeviceInfo.firm_version.in_(low_firm_version),
            DeviceInfo.firm_version_target != firm_version).scalar()
        if device_num == 0:
            return 0
        if percent == 100:
            limit = 2**32 - 1
        else:
            limit = device_num * percent / 100
        if limit == 0:
            return 0
        count = 0
        for _device in session.query(DeviceInfo) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type,
                        DeviceInfo.firm_version < firm_version,
                        DeviceInfo.firm_version.in_(low_firm_version),
                        DeviceInfo.firm_version_target != firm_version) \
                .order_by(DeviceInfo.id.desc()) \
                .limit(limit):
            _device.firm_version_target = firm_version
            _device.firm_version_use_confirm = use_confirm
            _device.update_time = datetime.datetime.now()
            session.commit()
            count += 1
        return count


def update_device_alg_percent_with_alg_version(
        percent, alg_version, device_type, low_alg_version,
        create_update_rule, use_confirm):
    """Update device alg version.

    Args:
        percent (int): the percentage of all device that will be update.
        alg_version (string) alg version.
        low_alg_version (list): only update the version in the list.
        create_update_rule (boolean): True: create update rule

    Returns:
        True when update success whether False.
    """

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if create_update_rule:
            for low_version in low_alg_version:
                update_or_create_update_rule(
                    low_version, alg_version, 1, device_type, use_confirm)
        device_num = session.query(func.count(DeviceInfo.id)).filter(
            DeviceInfo.deleted == 0,
            DeviceInfo.device_type == device_type,
            DeviceInfo.alg_version < alg_version,
            DeviceInfo.alg_version.in_(low_alg_version),
            DeviceInfo.alg_version_target != alg_version).scalar()
        if device_num == 0:
            return 0
        if percent == 100:
            limit = 2**32 - 1
        else:
            limit = device_num * percent / 100
        if limit == 0:
            return 0
        count = 0
        for _device in session.query(DeviceInfo) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type,
                        DeviceInfo.alg_version < alg_version,
                        DeviceInfo.alg_version.in_(low_alg_version),
                        DeviceInfo.alg_version_target != alg_version) \
                .order_by(DeviceInfo.id.desc()) \
                .limit(limit):
            _device.alg_version_target = alg_version
            _device.alg_version_use_confirm = use_confirm
            _device.update_time = datetime.datetime.now()
            session.commit()
            count += 1
        return count


def online_alg_info_with_alg_version(alg_version, device_type):
    """Online update info.

    Args:
        alg_version (string): alg version

    Returns:
        dict of update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(AlgorithmInfo) \
                              .filter(
                                  AlgorithmInfo.deleted == 0,
                                  AlgorithmInfo.online == 0,
                                  AlgorithmInfo.device_type == device_type,
                                  AlgorithmInfo.alg_version == alg_version) \
                              .first()
        if _update_info is None:
            return None
        else:
            _update_info.online = 1
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_update_info)


def offline_alg_info_with_alg_version(alg_version, device_type):
    """Delete update info.

    Args:
        alg_version (string): alg version

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(AlgorithmInfo) \
                              .filter(
                                  AlgorithmInfo.deleted == 0,
                                  AlgorithmInfo.online == 1,
                                  AlgorithmInfo.device_type == device_type,
                                  AlgorithmInfo.alg_version == alg_version) \
                              .first()
        if _update_info is None:
            return False
        else:
            _update_info.online = 0
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return True


def get_all_latest_alg_info(device_type):
    """Get all latest alg info.

    Args:

    Returns:
        dict of latest alg info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        version_to_alg_info = {}
        for _alg_info in session.query(AlgorithmInfo) \
                                .filter(AlgorithmInfo.deleted == 0,
                                        AlgorithmInfo.device_type ==
                                        device_type) \
                                .order_by(AlgorithmInfo.alg_version.desc()):
            alg_info = model_to_dict(_alg_info)
            alg_info['device_num'] = 0
            alg_info['target_device_num'] = 0
            version_to_alg_info[alg_info['alg_version']] = alg_info
            ret.append(alg_info)
        for _version, _count in session \
                .query(DeviceInfo.alg_version,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.alg_version):
            if _version in version_to_alg_info:
                version_to_alg_info[_version]['device_num'] = _count
        for _version, _count in session \
                .query(DeviceInfo.alg_version_target,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.alg_version_target):
            if _version in version_to_alg_info:
                version_to_alg_info[_version]['target_device_num'] = _count
        return ret


def get_device_info_with_device_id(device_id, device_type):
    '''Get the maximum index with current page.

    Args:
        device_id (string): device id
    Returns:
        the update configuration of specify device.
    '''

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device = session.query(DeviceInfo) \
                  .filter(DeviceInfo.deleted == 0,
                          DeviceInfo.device_type == device_type,
                          DeviceInfo.device_id == device_id) \
                  .first()
        if _device is None:
            return None
        else:
            return model_to_dict(_device)


def get_active_device_stat(device_type):
    '''Get the active device stat.

    Args:
    Returns:
        the status dict of active devices.
    '''

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = {}
        for i in [10, 15, 30, 45, 60]:
            active_time = \
                datetime.datetime.now() - datetime.timedelta(minutes=i)
            ret[i] = session.query(func.count(DeviceInfo.id)) \
                            .filter(DeviceInfo.deleted == 0,
                                    DeviceInfo.device_type == device_type,
                                    DeviceInfo.update_time > active_time) \
                            .scalar()
        return ret


def update_active_devices_with_type(
        active_minute, version, update_type, device_type):
    '''Update the active device's firm version.

    Args:
        active_minute (int): active within active_minute.
        version (string): target firm version
    Returns:
        the number of updated devices.
    '''

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if update_type == 0:
            _update_info = session.query(FirmInfo) \
                                  .filter(FirmInfo.deleted == 0,
                                          FirmInfo.online == 1,
                                          FirmInfo.device_type == device_type,
                                          FirmInfo.firm_version == version) \
                            .first()
            if _update_info is None:
                return None
        elif update_type == 1:
            _update_info = session.query(AlgorithmInfo) \
                            .filter(AlgorithmInfo.deleted == 0,
                                    AlgorithmInfo.online == 1,
                                    AlgorithmInfo.device_type == device_type,
                                    AlgorithmInfo.alg_version == version) \
                            .first()
            if _update_info is None:
                return None
        else:
            _update_info = session.query(FpgaInfo) \
                            .filter(FpgaInfo.deleted == 0,
                                    FpgaInfo.online == 1,
                                    FpgaInfo.device_type == device_type,
                                    FpgaInfo.fpga_version == version) \
                            .first()
            if _update_info is None:
                return None

        count = 0
        active_time = \
            datetime.datetime.now() - datetime.timedelta(minutes=active_minute)
        for _device in session.query(DeviceInfo) \
                              .filter(DeviceInfo.deleted == 0,
                                      DeviceInfo.device_type == device_type,
                                      DeviceInfo.update_time > active_time):
            if update_type == 0 and _device.firm_version < version:
                _device.firm_version_target = version
            elif update_type == 1 and _device.alg_version < version:
                _device.alg_version_target = version
            elif update_type == 2 and _device.fpga_version < version:
                _device.fpga_version_target = version
            else:
                return None
            _device.update_time = datetime.datetime.now()
            session.commit()
            count += 1
        return count


def get_latest_fpga_info(device_type, version=''):
    """Get latest update info.

    Args:

    Returns:
        dict of latest update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        filters = [FpgaInfo.deleted == 0, FpgaInfo.online == 1,
                   FpgaInfo.device_type == device_type]
        if version:
            filters.append(FpgaInfo.fpga_version == version)
        _update_info = session.query(FpgaInfo) \
                              .filter(*filters) \
                              .order_by(
                                  FpgaInfo.fpga_version.desc()).first()
        if not _update_info:
            return None
        else:
            return model_to_dict(_update_info)


def update_device_fpga_version(device_id, device_type, use_confirm):
    """Update device fpga.

    Args:
        device_id (string): device id

    Returns:
        dict of device info or None.
    """
    latest_fpga_info = get_latest_fpga_info(device_type)
    if latest_fpga_info is None:
        return None
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_info = session.query(DeviceInfo) \
                              .filter(DeviceInfo.device_id == device_id,
                                      DeviceInfo.device_type == device_type,
                                      DeviceInfo.deleted == 0) \
                              .first()
        if _device_info is None:
            return None
        else:
            _device_info.fpga_version_target = \
                latest_fpga_info['fpga_version']
            _device_info.fpga_version_use_confirm = use_confirm
            _device_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_device_info)


def get_all_latest_fpga_info(device_type):
    """Get all latest fpga info.

    Args:

    Returns:
        dict of latest fpga info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        version_to_fpga_info = {}
        for _fpga_info in session.query(FpgaInfo) \
                                 .filter(FpgaInfo.deleted == 0,
                                         FpgaInfo.device_type == device_type) \
                                 .order_by(FpgaInfo.fpga_version.desc()):
            fpga_info = model_to_dict(_fpga_info)
            fpga_info['device_num'] = 0
            fpga_info['target_device_num'] = 0
            version_to_fpga_info[fpga_info['fpga_version']] = fpga_info
            ret.append(fpga_info)
        for _version, _count in session \
                .query(DeviceInfo.fpga_version,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.fpga_version):
            if _version in version_to_fpga_info:
                version_to_fpga_info[_version]['device_num'] = _count
        for _version, _count in session \
                .query(DeviceInfo.fpga_version_target,
                       func.count(DeviceInfo.id)) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type) \
                .group_by(DeviceInfo.fpga_version_target):
            if _version in version_to_fpga_info:
                version_to_fpga_info[_version]['target_device_num'] = _count
        return ret


def update_device_fpga_percent_with_fpga_version(
        percent, fpga_version, device_type, low_fpga_version,
        create_update_rule, use_confirm):
    """Update device fpga version.

    Args:
        percent (int): the percentage of all device that will be update.
        fpga_version (string) fpga version.
        low_fpga_version (list): only update the version in the list.
        create_update_rule (boolean): True: create update rule

    Returns:
        True when update success whether False.
    """

    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if create_update_rule:
            for low_version in low_fpga_version:
                update_or_create_update_rule(
                    low_version, fpga_version, 2, device_type, use_confirm)
        device_num = session.query(func.count(DeviceInfo.id)).filter(
            DeviceInfo.deleted == 0,
            DeviceInfo.device_type == device_type,
            DeviceInfo.fpga_version < fpga_version,
            DeviceInfo.fpga_version.in_(low_fpga_version),
            DeviceInfo.fpga_version_target != fpga_version).scalar()
        if device_num == 0:
            return 0
        if percent == 100:
            limit = 2**32 - 1
        else:
            limit = device_num * percent / 100
        if limit == 0:
            return 0
        count = 0
        for _device in session.query(DeviceInfo) \
                .filter(DeviceInfo.deleted == 0,
                        DeviceInfo.device_type == device_type,
                        DeviceInfo.fpga_version < fpga_version,
                        DeviceInfo.fpga_version.in_(low_fpga_version),
                        DeviceInfo.fpga_version_target != fpga_version) \
                .order_by(DeviceInfo.id.desc()) \
                .limit(limit):
            _device.fpga_version_target = fpga_version
            _device.fpga_version_use_confirm = use_confirm
            _device.update_time = datetime.datetime.now()
            session.commit()
            count += 1
        return count


def online_fpga_info_with_fpga_version(fpga_version, device_type):
    """Online update info.

    Args:
        fpga_version (string): fpga version

    Returns:
        dict of update info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(FpgaInfo) \
                              .filter(
                                  FpgaInfo.deleted == 0,
                                  FpgaInfo.online == 0,
                                  FpgaInfo.device_type == device_type,
                                  FpgaInfo.fpga_version == fpga_version) \
                              .first()
        if _update_info is None:
            return None
        else:
            _update_info.online = 1
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_update_info)


def offline_fpga_info_with_fpga_version(fpga_version, device_type):
    """Delete update info.

    Args:
        fpga_version (string): fpga version

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_info = session.query(FpgaInfo) \
                              .filter(
                                  FpgaInfo.deleted == 0,
                                  FpgaInfo.online == 1,
                                  FpgaInfo.device_type == device_type,
                                  FpgaInfo.fpga_version == fpga_version) \
                              .first()
        if _update_info is None:
            return False
        else:
            _update_info.online = 0
            _update_info.update_time = datetime.datetime.now()
            session.commit()
            return True


def upload_fpga_info(fpga_version, fpga_url, device_type, md5):
    """Upload fpga info.

    Args:
        fpga_version (string): fpga version.
        fpga_url (string) : download file path.

    Returns:
        dict of fpga info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _fpga_info = session.query(FpgaInfo) \
                           .filter(FpgaInfo.fpga_version == fpga_version,
                                   FpgaInfo.device_type == device_type) \
                           .first()
        if _fpga_info is None:
            _fpga_info = FpgaInfo()
            _fpga_info.create_time = datetime.datetime.now()
        _fpga_info.device_type = device_type
        _fpga_info.fpga_version = fpga_version
        _fpga_info.fpga_url = fpga_url
        _fpga_info.online = 1
        _fpga_info.deleted = 0
        _fpga_info.md5 = md5
        _fpga_info.update_time = datetime.datetime.now()
        session.add(_fpga_info)
        session.commit()
        return model_to_dict(_fpga_info)


def get_all_update_rule(device_type):
    """Get all update rule.

    Args:

    Returns:
        list of update rule.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _rule in session.query(UpdateRule) \
                            .filter(UpdateRule.deleted == 0,
                                    UpdateRule.device_type == device_type) \
                            .order_by(UpdateRule.version.asc()):
            ret.append(model_to_dict(_rule))
    return ret


def online_update_rule_with_version(version, device_type):
    """Online update rule.

    Args:
        version (string): fpga version

    Returns:
        dict of update rule or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_rule = session.query(UpdateRule) \
                              .filter(
                                  UpdateRule.deleted == 0,
                                  UpdateRule.online == 0,
                                  UpdateRule.device_type == device_type,
                                  UpdateRule.version == version) \
                              .first()
        if _update_rule is None:
            return None
        else:
            _update_rule.online = 1
            _update_rule.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_update_rule)


def offline_update_rule_with_version(version, device_type):
    """Delete update rule.

    Args:
        version (string): fpga version

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _update_rule = session.query(UpdateRule) \
                              .filter(
                                  UpdateRule.deleted == 0,
                                  UpdateRule.online == 1,
                                  UpdateRule.device_type == device_type,
                                  UpdateRule.version == version) \
                              .first()
        if _update_rule is None:
            return False
        else:
            _update_rule.online = 0
            _update_rule.update_time = datetime.datetime.now()
            session.commit()
            return True


def update_or_create_update_rule(
        version, version_target, update_type, device_type, use_confirm):
    """update or create update rule.

    Args:
        version (string): version
        version_target (string): version_target
        update_type (int): 0: firm 1: alg 2: fpga
        device_type (int): 0: chigo 1: xiaoke 2: dianki 3: dianki_v4

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        if update_type == 0:
            version_info = get_latest_firm_info(device_type, version)
            version_target_info = \
                get_latest_firm_info(device_type, version_target)
        elif update_type == 1:
            version_info = get_latest_alg_info(device_type, version)
            version_target_info = \
                get_latest_alg_info(device_type, version_target)
        elif update_type == 2:
            version_info = get_latest_fpga_info(device_type, version)
            version_target_info = \
                get_latest_fpga_info(device_type, version_target)
        else:
            return u'版本号不存在'
        if not version_info or not version_target_info:
            return u'版本号不存在'

        _update_rule = session.query(UpdateRule) \
                              .filter(
                                  UpdateRule.device_type == device_type,
                                  UpdateRule.version == version) \
                              .first()
        if _update_rule is None:
            _update_rule = UpdateRule()
            _update_rule.create_time = datetime.datetime.now()
        _update_rule.version = version
        _update_rule.version_target = version_target
        _update_rule.update_type = update_type
        _update_rule.device_type = device_type
        _update_rule.use_confirm = use_confirm
        _update_rule.online = 1
        _update_rule.deleted = 0,
        _update_rule.update_time = datetime.datetime.now()
        session.add(_update_rule)
        session.commit()
        return u'创建成功'


def get_fpga_version_map_with_version_number(device_type, version_number):
    """Get all fpga version map.

    Args:

    Returns:
        list of version map.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _map = session.query(FpgaVersionMap) \
                      .filter(FpgaVersionMap.deleted == 0,
                              FpgaVersionMap.version_number == version_number,
                              FpgaVersionMap.device_type == device_type) \
                      .first()
        if _map is None:
            return None
        else:
            return model_to_dict(_map)


def get_all_fpga_version_map(device_type):
    """Get all fpga version map.

    Args:

    Returns:
        list of version map.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _map in session.query(FpgaVersionMap) \
                           .filter(FpgaVersionMap.deleted == 0,
                                   FpgaVersionMap.device_type == device_type) \
                           .order_by(FpgaVersionMap.version.desc()):
            ret.append(model_to_dict(_map))
    return ret


def update_or_create_fpga_version_map(
        version, version_number, device_type):
    """update or create fpga version map.

    Args:
        version (string): version
        version_number (string): version_number
        device_type (int): 0: chigo 1: xiaoke 2: dianki 3: dianki_v4

    Returns:
        string.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        version_info = get_latest_fpga_info(device_type, version)
        if version_info is None:
            return u'版本号不存在'
        _version_map = session.query(FpgaVersionMap) \
                              .filter(
                                  FpgaVersionMap.device_type == device_type,
                                  FpgaVersionMap.version == version) \
                              .first()
        if _version_map is None:
            _version_map = FpgaVersionMap()
            _version_map.create_time = datetime.datetime.now()
        _version_map.version = version
        _version_map.version_number = version_number
        _version_map.device_type = device_type
        _version_map.online = 1
        _version_map.deleted = 0,
        _version_map.update_time = datetime.datetime.now()
        session.add(_version_map)
        session.commit()
        return u'创建成功'


def online_fpga_version_map_with_version(version, device_type):
    """Online update rule.

    Args:
        version (string): fpga version

    Returns:
        dict of update rule or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _fpga_version_map = session.query(FpgaVersionMap) \
                              .filter(
                                  FpgaVersionMap.deleted == 0,
                                  FpgaVersionMap.online == 0,
                                  FpgaVersionMap.device_type == device_type,
                                  FpgaVersionMap.version == version) \
                              .first()
        if _fpga_version_map is None:
            return None
        else:
            _fpga_version_map.online = 1
            _fpga_version_map.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_fpga_version_map)


def offline_fpga_version_map_with_version(version, device_type):
    """Delete update rule.

    Args:
        version (string): fpga version

    Returns:
        True when delete success whether False.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _fpga_version_map = session.query(FpgaVersionMap) \
                              .filter(
                                  FpgaVersionMap.deleted == 0,
                                  FpgaVersionMap.online == 1,
                                  FpgaVersionMap.device_type == device_type,
                                  FpgaVersionMap.version == version) \
                              .first()
        if _fpga_version_map is None:
            return False
        else:
            _fpga_version_map.online = 0
            _fpga_version_map.update_time = datetime.datetime.now()
            session.commit()
            return True


def get_all_device_types():
    """Get all device type.

    Args:

    Returns:
        dict of device type info.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _device_type in session.query(DeviceType) \
                                   .order_by(DeviceType.id.desc()):
            _device_type_info = {}
            _device_type_info['id'] = _device_type.id
            _device_type_info['name'] = _device_type.name
            _device_type_info['device_name'] = _device_type.device_name
            ret.append(_device_type_info)
        return ret


def insert_device_type(name, device_name, email_address):
    """Add a device type.

    Args:
        name (string)
        device_name (string)
        email_address (string)
    Returns:
        string indicate insert result
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _device_type = session.query(DeviceType) \
                              .filter(DeviceType.name.like(name + '%')) \
                              .first()
        if _device_type:
            return u'添加失败,' + name + u'已存在或已有设备名包含' + name
        _device_type = session.query(DeviceType) \
                              .filter(DeviceType.device_name.like(device_name + '%')) \
                              .first()
        if _device_type:
            return u'添加失败,' + device_name + u'已存在或已有设备名包含' + device_name
        _device_type = DeviceType()
        _device_type.name = name
        _device_type.device_name = device_name
        _device_type.create_time = datetime.datetime.now()
        _device_type.update_time = _device_type.create_time
        session.add(_device_type)
        session.commit()
        _user = session.query(User) \
                       .filter(User.deleted == 0,
                               User.email_address == email_address) \
                       .first()
        _user.device_type_ids += (',' + str(_device_type.id))
        session.commit()
        return u'添加成功'
