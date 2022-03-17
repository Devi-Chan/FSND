/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000/', // the running FLASK api server url
  auth0: {
    url: 'dev--mvz-3ey.us', // the auth0 domain prefix
    audience: 'Shop', // the audience set for the auth0 app
    clientId: 'hVI8A7rQYAZieT6vUS0pBFp0Mfv0iCmE', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:8100/tabs/user-page', // the base url of the running ionic application. 
  }
};
