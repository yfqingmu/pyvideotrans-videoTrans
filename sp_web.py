from flask import Flask, jsonify, request
import threading
import os
import subprocess

app = Flask(__name__)

# 启动PyVideoTrans的功能
@app.route('/run', methods=['GET'])
def run_pyvideotrans():
    try:
        # 启动sp.py逻辑
        result = subprocess.Popen(['python3', 'sp.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify({"message": "PyVideoTrans started successfully!", "pid": result.pid})
    except Exception as e:
        return jsonify({"error": str(e)})

# 测试服务是否可用
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the PyVideoTrans Web Interface!"})

def start_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # 使用线程启动Flask服务
    threading.Thread(target=start_flask).start()
