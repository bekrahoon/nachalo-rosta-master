import { useSelector, useDispatch } from 'react-redux';
import {
  loginThunk,
  logoutThunk,
  registerThunk,
  getProfileThunk,
  updateProfileThunk,
  verifyEmailThunk,
  changePasswordThunk,
  requestPasswordResetThunk,
  confirmPasswordResetThunk,
  clearError,
  clearMessage,
} from '../store/authSlice';

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading, error, message } = useSelector(
    (state) => state.auth
  );

  const login = async (email, password) => {
    return dispatch(loginThunk({ email, password }));
  };

  const register = async (data) => {
    return dispatch(registerThunk(data));
  };

  const logout = async () => {
    return dispatch(logoutThunk());
  };

  const getProfile = async () => {
    return dispatch(getProfileThunk());
  };

  const updateProfile = async (data) => {
    return dispatch(updateProfileThunk(data));
  };

  const verifyEmail = async (token) => {
    return dispatch(verifyEmailThunk(token));
  };

  const changePassword = async (data) => {
    return dispatch(changePasswordThunk(data));
  };

  const requestPasswordReset = async (email) => {
    return dispatch(requestPasswordResetThunk(email));
  };

  const confirmPasswordReset = async (data) => {
    return dispatch(confirmPasswordResetThunk(data));
  };

  const handleClearError = () => {
    dispatch(clearError());
  };

  const handleClearMessage = () => {
    dispatch(clearMessage());
  };

  return {
    user,
    isAuthenticated,
    loading,
    error,
    message,
    login,
    register,
    logout,
    getProfile,
    updateProfile,
    verifyEmail,
    changePassword,
    requestPasswordReset,
    confirmPasswordReset,
    clearError: handleClearError,
    clearMessage: handleClearMessage,
  };
};
