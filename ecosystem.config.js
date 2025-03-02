module.exports = {
  apps: [{
    name: 'bg-remover',
    script: 'app.py',
    interpreter: 'python3',
    cwd: __dirname,
    env: {
      FLASK_ENV: 'production'
    },
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    merge_logs: true
  }]
};