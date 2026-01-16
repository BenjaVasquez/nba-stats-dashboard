const fetch = require('node-fetch');

exports.handler = async function (event, context) {
  // Asegúrate de que estas variables coincidan exactamente con tu GitHub
  const GITHUB_USER = 'BenjaVasquez';
  const REPO_NAME = 'nba-stats-dashboard';
  const TOKEN = process.env.GITHUB_TOKEN; // Este se configura en el panel de Netlify

  console.log('Intentando activar workflow en:', GITHUB_USER, REPO_NAME);

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

    if (response.ok) {
      return { statusCode: 200, body: 'Señal enviada correctamente' };
    } else {
      const errorText = await response.text();
      return { statusCode: response.status, body: errorText };
    }
  } catch (error) {
    return { statusCode: 500, body: error.toString() };
  }
};
