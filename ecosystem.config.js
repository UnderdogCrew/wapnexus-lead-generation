module.exports = {
    apps: [{
        name: 'lead-service',
        script: '/opt/python_apis/lead/bin/python',
        args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8002',
        interpreter: 'none',
        cwd: '/opt/python_apis/wapnexus-lead-generation',
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '1G'
    }]
};