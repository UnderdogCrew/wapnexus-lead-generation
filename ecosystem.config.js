module.exports = {
    apps: [{
        name: 'lead-service',
        script: '/opt/python_apis/lead/bin/python',
        args: 'uvicorn app.main:app --reload --port 8002',
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '1G'
    }]
};