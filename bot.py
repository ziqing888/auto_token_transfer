import random
import secrets
from web3 import Web3
from colorama import Fore, Style, init
import time
import getpass

# 初始化 colorama
init(autoreset=True)

def print_header():
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + "自动发送本地代币工具".center(50))
    print(Fore.YELLOW + "支持 EVM 链".center(50))
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)
    
# 转账函数
def TransferNative(sender, senderkey, recipient, amount, web3, retries=3):
    for attempt in range(retries):
        try:
            # 构建交易
            gas_tx = {
                'chainId': web3.eth.chain_id,
                'from': sender,
                'to': recipient,
                'value': web3.to_wei(amount, 'ether'),
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(sender)
            }
            gasAmount = web3.eth.estimate_gas(gas_tx)

            auto_tx = {
                'chainId': web3.eth.chain_id,
                'from': sender,
                'gas': gasAmount,
                'to': recipient,
                'value': web3.to_wei(amount, 'ether'),
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(sender)
            }

            fixamount = '%.18f' % float(amount)
            # 签名交易
            sign_txn = web3.eth.account.sign_transaction(auto_tx, senderkey)
            # 发送交易
            print(Fore.CYAN + f'正在发送 {fixamount} ETH 到随机地址: {recipient} ...')
            tx_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)

            # 获取交易哈希
            txid = str(web3.to_hex(tx_hash))
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(Fore.GREEN + f'成功发送 {fixamount} ETH 到地址: {recipient}!')
            print(Fore.GREEN + f'交易哈希: {txid}')

            # 显示剩余余额
            balance = web3.eth.get_balance(sender)
            balance_in_ether = web3.from_wei(balance, 'ether')
            print(Fore.CYAN + f"账户 {sender} 的剩余余额: {balance_in_ether} ETH")

            break
        except Exception as e:
            print(Fore.RED + f"尝试 {attempt + 1} 时出错: {e}")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"5 秒后重试... ({attempt + 1}/{retries})")
                time.sleep(5)
            else:
                print(Fore.RED + f"在尝试 {retries} 次后交易失败。")

# 生成随机接收地址
def generate_random_recipient(web3):
    priv = secrets.token_hex(32)  # 生成一个新的私钥
    private_key = "0x" + priv
    recipient = web3.eth.account.from_key(private_key)
    return recipient

# 检查 RPC URL 是否有效
def check_rpc_url(rpc_url, retries=3):
    for attempt in range(retries):
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if web3.is_connected():
                print(Fore.GREEN + "成功连接到 RPC 节点！")
                chain_id = web3.eth.chain_id  # 获取链 ID
                print(Fore.CYAN + f"链 ID: {chain_id}")
                return web3
            else:
                print(Fore.RED + "无法连接到 RPC 节点，请检查 URL。")
                if attempt < retries - 1:
                    print(Fore.YELLOW + f"5 秒后重试... ({attempt + 1}/{retries})")
                    time.sleep(5)
        except Exception as e:
            print(Fore.RED + f"连接 RPC 节点时出错 (第 {attempt + 1} 次): {e}")
            if attempt < retries - 1:
                print(Fore.YELLOW + f"5 秒后重试... ({attempt + 1}/{retries})")
                time.sleep(5)
        if attempt == retries - 1:
            print(Fore.RED + f"尝试 {retries} 次后仍无法连接到 RPC 节点。")
            return None

# 主程序
print_header()
# 输入并检查 RPC URL
web3 = None
while not web3:
    rpc_url = input("请输入 RPC URL: ")
    web3 = check_rpc_url(rpc_url)

# 安全输入用户私钥
private_key = getpass.getpass("请输入您的私钥（输入将隐藏）: ")
try:
    sender = web3.eth.account.from_key(private_key)
except Exception as e:
    print(Fore.RED + f"私钥无效: {e}")
    exit()

# 输入交易次数
while True:
    try:
        loop = int(input("请输入需要处理的交易次数: "))
        if loop > 0:
            break
        else:
            print(Fore.RED + "交易次数必须为正整数！")
    except ValueError:
        print(Fore.RED + "请输入有效的数字！")

# 输入每笔交易金额
while True:
    try:
        amount = float(input("请输入每笔交易的 ETH 数量（例如 0.001）: "))
        if amount > 0:
            break
        else:
            print(Fore.RED + "金额必须为正数！")
    except ValueError:
        print(Fore.RED + "请输入有效的金额！")

# 开始执行交易
for i in range(loop):
    print(Fore.CYAN + f"\n正在处理第 {i + 1}/{loop} 笔交易")
    
    # 为每笔交易生成一个随机接收地址
    recipient = generate_random_recipient(web3)
    
    # 使用发送方地址和私钥转账
    TransferNative(sender.address, private_key, recipient.address, amount, web3)

print(Fore.GREEN + "\n所有交易已完成。")
