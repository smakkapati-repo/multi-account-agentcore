// Environment-based configuration
export const API_URL = process.env.REACT_APP_GATEWAY_URL || 'http://localhost:3001';
export const ENVIRONMENT = process.env.NODE_ENV || 'production';

export const cognitoConfig = {
  region: process.env.REACT_APP_COGNITO_REGION || 'us-east-1',
  userPoolId: process.env.REACT_APP_USER_POOL_ID || '',
  userPoolWebClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || '',
  oauth: {
    domain: process.env.REACT_APP_COGNITO_DOMAIN || '',
    scope: ['email', 'openid', 'profile'],
    redirectSignIn: process.env.NODE_ENV === 'development'
      ? 'http://localhost:3000'
      : window.location.origin,
    redirectSignOut: process.env.NODE_ENV === 'development'
      ? 'http://localhost:3000'
      : window.location.origin,
    responseType: 'code'
  }
};
