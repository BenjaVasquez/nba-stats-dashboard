const fetch = require('node-fetch');

exports.handler = async function (event, context) {
  const TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_USER = 'BenjaVasquez';
  const REPO_NAME = 'nba-stats-dashboard';

  try {
    const response = await fetch(
      `https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/dispatches`,
      {
        method: 'POST',
        headers: {
          Authorization: `token ${TOKEN}`,
          Accept: 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ event_type: 'trigger-update' }),
      }
    );
    return { statusCode: 200, body: 'Señal enviada a GitHub' };
  } catch (error) {
    return { statusCode: 500, body: error.toString() };
  }
};
