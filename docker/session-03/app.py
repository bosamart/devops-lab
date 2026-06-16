from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello from bosamart DevOps Lab v2!</h1><p>CI/CD pipeline working!</p>''

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
