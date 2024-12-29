from flask import Flask, jsonify, request
import subprocess
import os

app = Flask(__name__)

# 启动 PyVideoTrans 的功能
@app.route('/run', methods=['GET'])
def run_pyvideotrans():
    try:
        # 使用相对路径运行 sp.py
        result = subprocess.Popen(['python3', 'sp.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify({"message": "PyVideoTrans started successfully!", "pid": result.pid})
    except Exception as e:
        return jsonify({"error": str(e)})

# 测试服务是否可用
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the PyVideoTrans Web Interface!"})

if __name__ == "__main__":
    # 运行 Flask 服务
    app.run(host='0.0.0.0', port=5000)
