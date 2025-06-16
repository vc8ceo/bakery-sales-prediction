import React, { useState } from 'react';
import { Container, Box, Typography } from '@mui/material';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          🥖 パン屋売上予測システム
        </Typography>
        
        <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
          POSレジデータと天気予報を活用した次営業日の売上・来店客数予測
        </Typography>

        {isLogin ? (
          <LoginForm onToggleMode={toggleMode} />
        ) : (
          <RegisterForm onToggleMode={toggleMode} />
        )}
      </Box>
    </Container>
  );
};

export default AuthPage;