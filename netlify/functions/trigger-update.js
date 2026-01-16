const fetch = require('node-fetch');
exports.handler = async function (event, context) {
  const response = await fetch(
    `https://api.github.com/repos/BenjaVasquez/nba-stats-dashboard/dispatches`,
    {
      method: 'POST',
      headers: {
        Authorization: `token ${process.env.GITHUB_TOKEN}`,
        Accept: 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ event_type: 'trigger-update' }),
    }
  );
  return { statusCode: 200, body: 'OK' };
};
