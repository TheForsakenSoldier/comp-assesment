
// javascript/containers/master-page.jsx
import React from 'react';
import MainContainer from './main-container';
import MainNavBar from './navbars/main-page-navbar';
import '../styles/main.css'; // Update the relative path to the CSS file


export default function RootContainer() {
  return (
    <>
        <MainNavBar />
      <MainContainer />
    </>
  );
}