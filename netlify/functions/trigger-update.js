// ELIMINAMOS la línea de 'require' porque Netlify ya tiene fetch global
exports.handler = async function (event, context) {
  const TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_USER = 'BenjaVasquez';
  const REPO_NAME = 'nba-stats-dashboard';

  try {
    // Usamos el fetch global (Node.js 18+ lo tiene por defecto)
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
      return { statusCode: 200, body: 'Señal enviada con éxito' };
    } else {
      const errorText = await response.text();
      return { statusCode: response.status, body: errorText };
    }
  } catch (error) {
    return { statusCode: 500, body: error.toString() };
  }
};
