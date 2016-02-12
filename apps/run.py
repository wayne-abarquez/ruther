from app import app
app.logger.info('Starting app')

if __name__ == '__main__':
    app.logger.info('App is being running from command line.....')
    app.run('0.0.0.0')