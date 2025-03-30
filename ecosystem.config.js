module.exports = {
  apps: [{
    name: 'bg-remover',
    script: 'gunicorn',
    args: '--bind 0.0.0.0:5000 --log-level=info app:app',
    interpreter: './venv/bin/python3',
    cwd: __dirname,
    env: {
      FLASK_ENV: 'production',
      LOG_LEVEL: 'INFO'
    },
    out_file: './logs/out.log',
    error_file: './logs/error.log'
  }]
};
