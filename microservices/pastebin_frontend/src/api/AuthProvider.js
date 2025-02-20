import { Auth0Provider } from "@auth0/auth0-react";

const AuthProvider = ({ children }) => {
  return (
    <Auth0Provider
      domain="dev-0yikj7u0gbje0gor.us.auth0.com"
      clientId="k32VuREqw6RlMXsOgMK1EJwZ6T3rZkjW"
      authorizationParams={{ redirect_uri: window.location.origin }}
    >
      {children}
    </Auth0Provider>
  );
};

export default AuthProvider;
