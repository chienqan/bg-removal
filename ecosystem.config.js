module.exports = {
  apps: [{
    name: 'bg-remover',
    script: 'gunicorn',
    args: '--bind 0.0.0.0:5000 --log-level=info --access-logfile=./logs/gunicorn_access.log --error-logfile=./logs/gunicorn_error.log app:app',
    interpreter: './venv/bin/python3',
    cwd: __dirname,
    env: {
      FLASK_ENV: 'production',
      LOG_LEVEL: 'INFO',
      HOST: '0.0.0.0',
      PORT: '5000'
    },
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    merge_logs: true,
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
