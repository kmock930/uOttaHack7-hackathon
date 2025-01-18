import React from "react";
import ReactDOM from "react-dom/client";
import { GlobalStyles } from '@bigcommerce/big-design';
import { theme } from '@bigcommerce/big-design-theme';
import { ThemeProvider } from 'styled-components';
import App from "./components/App";

 
const container = document.getElementById("root");
if (!container) throw new Error("Failed to find #root element - please check your HTML file includes a <div id=\"root\"></div>");
  
 
ReactDOM.createRoot(container!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
