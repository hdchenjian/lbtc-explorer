#!/usr/bin/env python3
# encoding: utf-8

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
import time

send_from_address = None
wallat_address = ['11rbR5AUptzP85Vpu2Po6YWwPE59zcNPv', '115KTum5Rpy8JrVGyQLWMB85rsjgiixkt8', '1bQSbEb7R4tWHF6iyPShh561evR2HeU8w', '1j8ywSEfXtHUU31pt5cwTFehF7PfxgwW4', '1pBiobvYXDxTzsKzgyb78xG3BTruFnx4Q', '1yTCoM3HrResVW8uJ8VxjZFo1g9B89Jy6', '12qZDWm2m5PvAx2FvUzuCa6rnmACXvWcHt', '12qdM4KXzcrLvqk8TFSMrEY4G5Q8HP6ZQE', '133zxWubnyrRFAGTTAyRnV2Ddi84FPLeUp', '13LawAPVWEnqHVLcshCYFj14EyEopCgWV4', '13Mv2Ba1MKosQUqwhKvqgHbMdiHcGG1MvK', '13NPMTRQBYvPL3gmTGiNA9bj4hJ61PsAm4', '13zogRwRPwLhuquhMh6Vj3frvt7Qg7QYhe', '1411KFyj4vjsTtjL4jNEt1KRqz2aQkrDV9', '142BwQ2iKCzMYwoh5HMC6i6uNb5qRwuM3u', '143uPZi4ir35PFWWWPzSYyg74tLLgqTaeg', '148HiXNjhDDsLCyuasJLLhTijAvP2qYGQo', '14DXyfysqV1pLYzKsq16pF7251E1PgYXjb', '14FAX57fwrgyte7d4YezfpqQWJQ6tTbxoR', '14LDyPNd2LKgXSakHBBDEFnX26RmuBWvqE', '14NEagNSCNjRjzhnNxvCdHBe83PRsaFzAf', '14NheBNdjHW2DZKDAkkRHkQLcuYbmA6X8z', '14VrioMdRoS4EbThGdhLzLZifX8T9ALGm2', '14b3ZJD1CWkAdoeTFZ5w1R8VBRsucpkfPu', '14chjTzgy8dstAxoBHaufdi63vxgBFwSHQ', '14kwFcnAkZtWiUoaycZhUyDhyvzXzHAHoN', '14nmyzEKbv9DPARzYB59qZLLy33m6yS2nV', '14wkP4WQfwLa61GLyw7FNgcSGtijZ9vwGU', '159JrhijHkyh66H6NofiSgxnfrawnkCMY7', '15MPc4pbCFScWQeSMoCnMvYjbH1d2xCYXR', '15WzKNHotoMashCGbs9DmZFmk1yVYa8xsm', '15eFbokXZkLiyWMBj1CrQuuWN4uXqgW4QE', '15evdSPpfPNrZYZfJ8C6Vet5eB7i8BvZ1t', '15kBBi9sE8pbMxsmYWNmhqww2JBZCLAjch', '166oK9a6uhKxpxA2CzAgr1tfvXoxTCcvWc', '16B7ei3GBA3bLrnPRfYAmtwKVH4QgJMwZs', '16Wjw38NBsa3f24i9oEMxpncVQC59w5apE', '16nm8W3M6e4dfTuwFnPcTfgnUbHWMdn9YJ', '16oHLyvZZQmJ89zTKFHq7HkaPotKgahzxK', '172c2moUqRqrwxr5XN7guTfXkCtnxsjCbS', '174DB1PXZAtJBWVXCfXZjuTggVUmhkwrK4', '17AWKgLXN49sgdvyPaP5h52XyieMzRGqrC', '17E14rhf6uEUsr7cuC8QYMrbb1g37iXE9M', '17JYLtJwWsCd26PTByykWD2a4seP9jGXnP', '17gSvVQBy9ch2NH1w7d5hbQBcPu2DHHwKH', '17nKrztN6wMfHxXeUupcGR9WdMhzzzGB8k', '18B6W83Xwtw4Psk4vtCXSDFLsjoGocy33Y', '18DEsGeniUYHwZZFSw8WQoFTT1RcFT6TTV', '18JWi8Mtftiarc4HoCWa1G5V3r8akgisbd', '18S9kCHMM4ngJkNxKzwfdTByDQhQZJCY3P', '18qxCah3PTVTdiqWdEWbxX4gQtbLrZksj3', '18sry44UBBMUCmqagy4QvpGA2exM9C2pqB', '195w43sdTHX6siC25ze5ySBLvbnZseGujp', '195xHNVUVEP1cv7eLTbBzZBCeTKJM7Qzim', '198BFnPYD3yDAx6GoxxGBRZNPm8V8bypWX', '19Lik6YVqQcmSc3x2XrofeHeM5jUBxRCLs', '19XPV2a9JCDAaKbQNNaidTZij86WDS3nzH', '1ARLgBAr1FjH5S94tbNAogRuCf5TESwcRY', '1AdoncLpC2tx5T7nYa9SzJP9RdfTvhnUzb', '1AgRectF1xX6abTAxWV1PZt9WvuyNQW4ex', '1AtbGkMAxzMtw9RNAoWeWH8d5nWMFZEwww', '1B6GAjZ6QDhv1QpUsA6cc96ksT1Gz2LJkS', '1B8zjH4YfYj33qa2tqKdv8jrYQ2D9jyRJH', '1BE5gUnC5tDSw9apSkmFj95ZijKvJZRi3W', '1BQDs3MuRrusEmy62xAmwQZh4ha5CBcQ5q', '1BThtXYfUEau4aYYYSuyhEhp7rixpRRVyS', '1BZHwugJ6xLfpub5eUXv1LZAaUyGFA4kqm', '1Bp3riDiQrtSFwXJv8NRwk5ijAABTHRWqB', '1BwiViguid1YczkhiMEhCRxX4bsnMN2s4u', '1C5rdwms85KjQvxQ9J2y4HQFeqB6Xenk3x', '1C75M9nNmMp3SD3p79zioHHYHdwZBiCWPa', '1CBub9G9BGRfjuK1eV2i4jHYapzZnSCkfC', '1CFqdpqzD1asYJNP6cTxgKjKamR4oSkQ35', '1CSqREQZKSjcMCuYA6uLT2BUmGtVS6EFzx', '1CUZR3V3o5wydAVhqSLLY2hbcJJARA52DB', '1Cg2eY4Bg2eDpJmaJs4RBWeg9eCx3vLgVR', '1CoDaQoKSd9LFQVR4pFgu8yqD4wbiFg9yJ', '1CuqmwbmDp4g1pMZC5uJwZJhRgA3ctgQJW', '1D7ksLCCugpU7oD87eT8VeM77FE5jEB5BQ', '1DAUFdk9HkdhMR9qsNEtws3JApnug9g4mg', '1DJfSAE2DeGggWPjg2joujxQsMP3PY5aWo', '1DL81WB6Bfv8GJnTW3LK4hnuygHpjbUBN6', '1DLEeGLihHAVMG8y8GwmxjK3XSBnCuQUMz', '1DRsB3tCypA2YVpCa5KArUQZW4YYJqLo2S', '1DT3Dr6HvTJsHBzL2FCiGZVKyHQa2GtW5b', '1DeeDXiR93nKb7dHRZ23tucP15y7yw46RL', '1DiDkezAZ3cVU95MpQTDrq1u6KT18vxhUo', '1EPyvaiMF1QiwYtqSYgHJmFLhw42ggz4B1', '1EXRrJ1UgAntHA92eVWxn8D5fFRD2M4EHy', '1Ejc3SAj9ng1fys12TPmFjNqN97gmwCmfU', '1FS8GEBwyBQzzaaNswnncx73cc1K3Ap3TL', '1FjpFDS423SvaPJRXHRVZJq3FwQqW3Rqnp', '1FnKZnjH3FVd8fQmotz3QEaWjEMX7gyMwU', '1FuC5w1ERoyYkc33A7Vcph1i8YHMhsokqn', '1GAiDdB1RZup987pUHecDE8bEvVqvxuSMr', '1GSVKRG3Dh3NAEAvNgj9quaQeE7RoN8dEb', '1GV7CeAc8XJszNGuJ1BzriiRjhYDgT5BMX', '1GXLJ8qaQGigziRpEVWYkDHkjMCkB9UWsA', '1GbfFDMGQC7A9w3A8ZYCYMY9ts3kaNS7Uk', '1GhU5zbsZfLzyHBPDLk73kjitWKdRVYMU3', '1GpcbnjStfViBpj9PyKro3XMTcq2dnHy7U', '1HKxcTYzLzyrsHaG6JL5XgzCw2a9SEZRbd', '1HTMo7fHjGwXqxtDDxf1otNJXR8KSeBnjD', '1HU954uZ58GQ9Kzj8QeegVJZPK89g6aDti', '1HUxFMEMWVt8Pnfqa4QffHeVDHzG6w6t8j', '1HWcZGBNUQCXZ9SUPg2LgaWMBVECwsYXqu', '1HfVNuVb5ycd6LY8mbZZPLNrqS6DFzA89C', '1HmtYDwpbqjSfMF1DKmehv845eRHL47EuJ', '1HqHNkWk3C9XRcrhTY9edhTrPLi43scbXA', '1HwmsW1Y1c4CGS6BFYJNgUv8Jq4CRnrrxj', '1J5UaGk2uwQyxeJRHijT26MSYVbGbt9V9k', '1JL6n4EmLkP3eYn2U77Argf2eF7bMJwxiH', '1JQk1aKcoeqbQMepAgQebxmrFQuxniANko', '1JUmtN6ALmUWHnEqZJTLXoDvhUZyeEV71a', '1JYYQr6BtVu8vu65seZa62jEdeEbVi5AAk', '1JcrTojqgz1KrHXf5cyDRobErXDukT13Lg', '1JgXTDJRnHcNdz7F6At2mowX5CTvDjzTHu', '1JkU9XHR92fQiVG1FTsBQwggTqYbatM5o8', '1JwwRMgbXvon3unPpgeQL4sAwZ1vZzVkH6', '1JyS9BiPoVkz14go299KPgFcGYxXe4ZQG2', '1KWEL7PiwwEcKy5Spu7xsy5oPUZKvULrW8', '1KYdzDQBdUZs5M5s7FGiZe136t7pqcmP3s', '1KpQzjDmR5CRmPWbfuFzvqzYuBqgXK9Ud2', '1L5sGU7SeFmRbLGFnusARGx2MZ3FXzXVo4', '1L7jMdPbQXeZGRdV9bVNAnK6CAMXK6n2dK', '1LGr41xCXWaxCR4YaJeqntBBSVHZ4gCtrF', '1LKUApLYCybHcFoMyFyYHe98fM2APiZoaM', '1LLLXogS9LLCMiDjo3iccZYXURn4M1rC8v', '1LQTMqMMayPSaPWqFuW6Bu9yQ1RCdatWyH', '1LQWF65cP3GMyEHBETktx64v8PBjisoto4', '1LYQwSEjb3Q1wZLnmRTAJieqVurypZ92Vw', '1LfxkBLrj5UJPZND799WbtwmmQrYSUFqyz', '1LrW8Q9RkXnoZrimoTERApb9X8E1NhRMm4', '1M8JsiPVbiYFE5zgYFqRYaAnFu3oUu52PC', '1MQGPV9xeHgaQPZLwYDQWecdH9thiB9ddq', '1MnyU3eRNTWmHG8fQ6GNQH1wep1rC7JqpC', '1MohN9NeE6TKyp2dmCNDUF5Rb3YBTHwGnc', '1N8fpDLsKW4RphLJas3BzxhMYMSSF3HzDB', '1NBSU2ogT5qBZ6LY3z8Bqq7CwiFwMgLyFm', '1NZ3pNMckpTGMdfacdv4ex4yZR4remGZz7', '1NbzXr1PeP9PpkCnYs5ZvV3nP3entgVaYp', '1NmLZa9fYhgSchkowPHMpbVe1dDxkdUe7m', '1NmrSJwP7SHLH3Y7Vwk66USxqyLavK8ceS', '1NqkTi3Nk7bGHnF1YUXUkXmtcRCqmep2x3', '1NzXkFN2VEzGxvkso58GK854uGWAm6Uwf3', '1PCSkxAPW6FhqkEid5fye2daPUez7ka7kd', '1PTc1UYzmfjExa3Z2eff24g7eMTDhrUvEm', '1PV5fUPErEvX3wAQBVhvsecnyYGzSUvF9D', '1PkdoWSGaWSpcTfcF2UyduwwSrZYc9q97T', '1PobEpa1gNDUbhQkKf4YTEPuxoNyujyud3']

@singleton('/tmp/update_rpc_node.pid')
def update_rpc_node():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        rpc_connection.settxfee(0.0001)
        print('balance' , rpc_connection.getbalance('lbtc'))
        print(rpc_connection.getwalletinfo())
        _address = None
        transform_amount = 0.000006
        for i in range(0, int(1000 / 7 + 2)):
            while(True):
                _address = rpc_connection.getnewaddress('lbtc')  # 1PV5fUPErEvX3wAQBVhvsecnyYGzSUvF9D
                if(rpc_connection.getaddressbalance(_address) == 0): break

            for item in wallat_address:
                if rpc_connection.getaddressbalance(item) > 1000:
                    send_from_address = item
                    break
            try:
                rpc_connection.sendfromaddress(send_from_address, _address, transform_amount)
                print('sendfromaddress', send_from_address, _address, transform_amount)
            except JSONRPCException as e:
                if e.error['message'] == 'Transaction amount too small':
                    print('JSONRPCException', e.error['message'])
                    transform_amount *= 1.2
                elif 'Insufficient funds' == e.error['message']:
                    print('JSONRPCException', e)
                    wallat_address.remove(send_from_address)
            except Exception as e:
                print(e)
            time.sleep(0.3)
        #print(rpc_connection.getaddressesbyaccount('lbtc'))
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    update_rpc_node()
