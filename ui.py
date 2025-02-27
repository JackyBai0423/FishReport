from pusher import push
from flask import Flask, render_template, request, jsonify
from threading import Thread

pusher = Thread(target=push)
pusher.start()

app = Flask(__name__)

@app.route('/')
def index():
    return "<p>欢迎使用WxPusher推送服务</p>"

app.run(host="localhost")


pusher.join()
