import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as authApi from '../api/auth';

// Преобразует ошибку DRF (объект с массивами сообщений по полям) в строку
const formatApiError = (data, fallback) => {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (Array.isArray(data)) return data.join(' ');
  if (typeof data === 'object') {
    return Object.values(data).flat().join(' ');
  }
  return fallback;
};

// Async thunks
export const loginThunk = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const data = await authApi.loginUser(email, password);
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      // Получаем профиль пользователя
      const profile = await authApi.getProfile();
      localStorage.setItem('user', JSON.stringify(profile));
      
      return profile;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const registerThunk = createAsyncThunk(
  'auth/register',
  async (data, { rejectWithValue }) => {
    try {
      const response = await authApi.registerUser(data);
      return response;
    } catch (error) {
      return rejectWithValue(formatApiError(error.response?.data, 'Registration failed'));
    }
  }
);

export const verifyEmailThunk = createAsyncThunk(
  'auth/verifyEmail',
  async (token, { rejectWithValue }) => {
    try {
      const data = await authApi.verifyEmail(token);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.token || 'Verification failed');
    }
  }
);

export const getProfileThunk = createAsyncThunk(
  'auth/getProfile',
  async (_, { rejectWithValue }) => {
    try {
      const data = await authApi.getProfile();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch profile');
    }
  }
);

export const updateProfileThunk = createAsyncThunk(
  'auth/updateProfile',
  async (data, { rejectWithValue }) => {
    try {
      const response = await authApi.updateProfile(data);
      const userData = response.user;
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    } catch (error) {
      return rejectWithValue(formatApiError(error.response?.data, 'Update failed'));
    }
  }
);

export const logoutThunk = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authApi.logoutUser(refreshToken);
      }
      
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      return null;
    } catch (error) {
      // Очищаем токены даже если logout не удался
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      return null;
    }
  }
);

export const changePasswordThunk = createAsyncThunk(
  'auth/changePassword',
  async (data, { rejectWithValue }) => {
    try {
      const response = await authApi.changePassword(data);
      return response;
    } catch (error) {
      return rejectWithValue(formatApiError(error.response?.data, 'Password change failed'));
    }
  }
);

export const requestPasswordResetThunk = createAsyncThunk(
  'auth/requestPasswordReset',
  async (email, { rejectWithValue }) => {
    try {
      const response = await authApi.requestPasswordReset(email);
      return response;
    } catch (error) {
      return rejectWithValue(formatApiError(error.response?.data, 'Request failed'));
    }
  }
);

export const confirmPasswordResetThunk = createAsyncThunk(
  'auth/confirmPasswordReset',
  async (data, { rejectWithValue }) => {
    try {
      const response = await authApi.confirmPasswordReset(data);
      return response;
    } catch (error) {
      return rejectWithValue(formatApiError(error.response?.data, 'Reset failed'));
    }
  }
);

// Initial state
const initialState = {
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,
  message: null,
};

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearMessage: (state) => {
      state.message = null;
    },
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    clearAuth: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      });

    // Register
    builder
      .addCase(registerThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.message = action.payload.message;
        state.error = null;
      })
      .addCase(registerThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Verify Email
    builder
      .addCase(verifyEmailThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyEmailThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.message = action.payload.message;
        state.error = null;
      })
      .addCase(verifyEmailThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Get Profile
    builder
      .addCase(getProfileThunk.pending, (state) => {
        state.loading = true;
      })
      .addCase(getProfileThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(getProfileThunk.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
      });

    // Update Profile
    builder
      .addCase(updateProfileThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfileThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.message = 'Profile updated successfully';
      })
      .addCase(updateProfileThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Logout
    builder
      .addCase(logoutThunk.pending, (state) => {
        state.loading = true;
      })
      .addCase(logoutThunk.fulfilled, (state) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
        state.error = null;
      })
      .addCase(logoutThunk.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
      });

    // Change Password
    builder
      .addCase(changePasswordThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(changePasswordThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.message = action.payload.message;
      })
      .addCase(changePasswordThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Request Password Reset
    builder
      .addCase(requestPasswordResetThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(requestPasswordResetThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.message = action.payload.message;
      })
      .addCase(requestPasswordResetThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Confirm Password Reset
    builder
      .addCase(confirmPasswordResetThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmPasswordResetThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.message = action.payload.message;
      })
      .addCase(confirmPasswordResetThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, clearMessage, setUser, clearAuth } = authSlice.actions;
export default authSlice.reducer;
