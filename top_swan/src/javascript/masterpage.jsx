//javascript/masterpage.jsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import RootContainer from "./containers/master-page-container";
import "./styles/main.css";
import 'bootstrap/dist/css/bootstrap.min.css';

// Get the root container
const domNode = document.getElementById('root');
// Create a root
const root = createRoot(domNode);
// Render the container
root.render(
 <RootContainer />
);