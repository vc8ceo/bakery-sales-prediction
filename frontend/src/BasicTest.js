import React from 'react';

function BasicTest() {
  return React.createElement('div', null, 
    React.createElement('h1', null, 'JavaScriptテスト'),
    React.createElement('p', null, 'このコンポーネントはJavaScriptで書かれています。')
  );
}

export default BasicTest;
