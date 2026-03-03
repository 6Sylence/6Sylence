import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { api } from '../../src/services/api';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
  success: '#4CAF50',
};

export default function ProfileScreen() {
  const router = useRouter();
  const { user, isAuthenticated, loading, login, logout } = useAuth();

  const handleBecomeSeller = async () => {
    if (!isAuthenticated) {
      Alert.alert('Inicia sesión', 'Debes iniciar sesión para convertirte en vendedor');
      return;
    }

    Alert.alert(
      'Convertirse en vendedor',
      '¿Deseas convertirte en vendedor? Podrás publicar y vender tus productos.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sí, quiero vender',
          onPress: async () => {
            try {
              await api.becomeSeller();
              Alert.alert('Éxito', '¡Ahora eres vendedor!');
              // Refresh user data
              window.location.reload();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'No se pudo procesar la solicitud');
            }
          },
        },
      ]
    );
  };

  const menuItems = [
    { icon: 'receipt-outline', label: 'Mis pedidos', route: '/orders' },
    { icon: 'heart-outline', label: 'Favoritos', route: '/favorites' },
    { icon: 'location-outline', label: 'Direcciones', route: '/addresses' },
    { icon: 'card-outline', label: 'Métodos de pago', route: '/payment-methods' },
    { icon: 'settings-outline', label: 'Configuración', route: '/settings' },
    { icon: 'help-circle-outline', label: 'Ayuda', route: '/help' },
  ];

  const sellerMenuItems = [
    { icon: 'storefront-outline', label: 'Panel de vendedor', route: '/seller/dashboard' },
    { icon: 'cube-outline', label: 'Mis productos', route: '/seller/products' },
    { icon: 'add-circle-outline', label: 'Añadir producto', route: '/seller/add-product' },
    { icon: 'stats-chart-outline', label: 'Estadísticas', route: '/seller/stats' },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mi Perfil</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Profile Card */}
        <View style={styles.profileCard}>
          {isAuthenticated && user ? (
            <>
              <View style={styles.avatarContainer}>
                {user.picture ? (
                  <Image source={{ uri: user.picture }} style={styles.avatar} />
                ) : (
                  <View style={styles.avatarPlaceholder}>
                    <Text style={styles.avatarText}>{user.name?.[0]?.toUpperCase() || 'U'}</Text>
                  </View>
                )}
                {user.role === 'seller' && (
                  <View style={styles.sellerBadge}>
                    <Ionicons name="checkmark-circle" size={20} color={COLORS.gold} />
                  </View>
                )}
              </View>
              <Text style={styles.userName}>{user.name}</Text>
              <Text style={styles.userEmail}>{user.email}</Text>
              {user.role === 'seller' && (
                <View style={styles.roleBadge}>
                  <Ionicons name="storefront" size={14} color={COLORS.gold} />
                  <Text style={styles.roleBadgeText}>Vendedor</Text>
                </View>
              )}
            </>
          ) : (
            <>
              <View style={styles.avatarPlaceholder}>
                <Ionicons name="person-outline" size={40} color={COLORS.gray} />
              </View>
              <Text style={styles.loginPrompt}>Inicia sesión para ver tu perfil</Text>
              <TouchableOpacity style={styles.loginButton} onPress={login}>
                <Ionicons name="logo-google" size={20} color={COLORS.white} />
                <Text style={styles.loginButtonText}>Continuar con Google</Text>
              </TouchableOpacity>
            </>
          )}
        </View>

        {/* Seller Section */}
        {isAuthenticated && user?.role === 'seller' && (
          <View style={styles.menuSection}>
            <Text style={styles.menuSectionTitle}>Panel de Vendedor</Text>
            {sellerMenuItems.map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.menuItem}
                onPress={() => router.push(item.route as any)}
              >
                <View style={[styles.menuIconContainer, { backgroundColor: COLORS.gold + '20' }]}>
                  <Ionicons name={item.icon as any} size={22} color={COLORS.gold} />
                </View>
                <Text style={styles.menuItemLabel}>{item.label}</Text>
                <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Become Seller */}
        {isAuthenticated && user?.role !== 'seller' && (
          <TouchableOpacity style={styles.becomeSellerCard} onPress={handleBecomeSeller}>
            <Ionicons name="storefront" size={32} color={COLORS.gold} />
            <View style={styles.becomeSellerInfo}>
              <Text style={styles.becomeSellerTitle}>Conviértete en vendedor</Text>
              <Text style={styles.becomeSellerSubtitle}>Vende tus productos y gana dinero</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color={COLORS.gold} />
          </TouchableOpacity>
        )}

        {/* Menu Items */}
        {isAuthenticated && (
          <View style={styles.menuSection}>
            <Text style={styles.menuSectionTitle}>Mi Cuenta</Text>
            {menuItems.map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.menuItem}
                onPress={() => router.push(item.route as any)}
              >
                <View style={styles.menuIconContainer}>
                  <Ionicons name={item.icon as any} size={22} color={COLORS.accent} />
                </View>
                <Text style={styles.menuItemLabel}>{item.label}</Text>
                <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Logout */}
        {isAuthenticated && (
          <TouchableOpacity style={styles.logoutButton} onPress={logout}>
            <Ionicons name="log-out-outline" size={22} color={COLORS.accent} />
            <Text style={styles.logoutText}>Cerrar sesión</Text>
          </TouchableOpacity>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primary,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.white,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 20,
  },
  profileCard: {
    backgroundColor: COLORS.white,
    marginHorizontal: 16,
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  avatarContainer: {
    position: 'relative',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  avatarPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 32,
    fontWeight: '700',
    color: COLORS.primary,
  },
  sellerBadge: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 2,
  },
  userName: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.text,
    marginTop: 12,
  },
  userEmail: {
    fontSize: 14,
    color: COLORS.gray,
    marginTop: 4,
  },
  roleBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.gold + '20',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginTop: 12,
    gap: 4,
  },
  roleBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.gold,
  },
  loginPrompt: {
    fontSize: 16,
    color: COLORS.gray,
    marginTop: 16,
  },
  loginButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.accent,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 16,
    gap: 8,
  },
  loginButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  becomeSellerCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    padding: 16,
    borderWidth: 2,
    borderColor: COLORS.gold,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  becomeSellerInfo: {
    flex: 1,
    marginLeft: 16,
  },
  becomeSellerTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.text,
  },
  becomeSellerSubtitle: {
    fontSize: 12,
    color: COLORS.gray,
    marginTop: 2,
  },
  menuSection: {
    marginTop: 24,
    paddingHorizontal: 16,
  },
  menuSectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.gray,
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
  },
  menuIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: COLORS.accent + '15',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuItemLabel: {
    flex: 1,
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.text,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 16,
    marginTop: 24,
    padding: 16,
    borderRadius: 12,
    backgroundColor: COLORS.accent + '10',
    gap: 8,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.accent,
  },
});
