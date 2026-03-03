import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../src/services/api';
import { useAuth } from '../../src/context/AuthContext';

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

export default function SellerProducts() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuth();

  const { data: products, isLoading } = useQuery({
    queryKey: ['seller', 'products'],
    queryFn: api.getSellerProducts,
    enabled: isAuthenticated && user?.role === 'seller',
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seller', 'products'] });
      Alert.alert('Éxito', 'Producto eliminado');
    },
    onError: (error: any) => {
      Alert.alert('Error', error.message || 'No se pudo eliminar el producto');
    },
  });

  const handleDelete = (productId: string, title: string) => {
    Alert.alert(
      'Eliminar producto',
      `¿Estás seguro de que quieres eliminar "${title}"?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: () => deleteMutation.mutate(productId),
        },
      ]
    );
  };

  if (!isAuthenticated || user?.role !== 'seller') {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color={COLORS.white} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Mis Productos</Text>
          <View style={{ width: 44 }} />
        </View>
        <View style={styles.emptyContainer}>
          <Ionicons name="lock-closed-outline" size={60} color={COLORS.gray} />
          <Text style={styles.emptyText}>Acceso restringido</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Mis Productos</Text>
        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => router.push('/seller/add-product')}
        >
          <Ionicons name="add" size={24} color={COLORS.white} />
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={COLORS.accent} />
          </View>
        ) : !products || products.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="cube-outline" size={60} color={COLORS.gray} />
            <Text style={styles.emptyText}>No tienes productos aún</Text>
            <TouchableOpacity
              style={styles.addProductBtn}
              onPress={() => router.push('/seller/add-product')}
            >
              <Text style={styles.addProductBtnText}>Añadir primer producto</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={styles.resultCount}>{products.length} productos</Text>
            {products.map((product: any) => (
              <View key={product.product_id} style={styles.productCard}>
                <View style={styles.productImage}>
                  <Ionicons name="cube-outline" size={32} color={COLORS.gray} />
                </View>
                <View style={styles.productInfo}>
                  <Text style={styles.productTitle} numberOfLines={2}>{product.title}</Text>
                  <Text style={styles.productPrice}>€{product.price.toFixed(2)}</Text>
                  <View style={styles.productMeta}>
                    <Text style={styles.productStock}>Stock: {product.stock}</Text>
                    <View style={styles.ratingContainer}>
                      <Ionicons name="star" size={12} color={COLORS.gold} />
                      <Text style={styles.productRating}>{product.rating.toFixed(1)}</Text>
                    </View>
                  </View>
                </View>
                <View style={styles.productActions}>
                  <TouchableOpacity
                    style={styles.actionBtn}
                    onPress={() => router.push(`/seller/edit-product?id=${product.product_id}`)}
                  >
                    <Ionicons name="create-outline" size={20} color={COLORS.primary} />
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.actionBtn, { backgroundColor: COLORS.accent + '15' }]}
                    onPress={() => handleDelete(product.product_id, product.title)}
                  >
                    <Ionicons name="trash-outline" size={20} color={COLORS.accent} />
                  </TouchableOpacity>
                </View>
              </View>
            ))}
            <View style={{ height: 100 }} />
          </ScrollView>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  addBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.white,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.gray,
    marginTop: 16,
    textAlign: 'center',
  },
  addProductBtn: {
    backgroundColor: COLORS.accent,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 20,
  },
  addProductBtnText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  resultCount: {
    fontSize: 14,
    color: COLORS.gray,
    paddingTop: 20,
    paddingBottom: 12,
  },
  productCard: {
    flexDirection: 'row',
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  productImage: {
    width: 70,
    height: 70,
    borderRadius: 12,
    backgroundColor: COLORS.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
  },
  productInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  productTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
  },
  productPrice: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.accent,
    marginTop: 4,
  },
  productMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    gap: 12,
  },
  productStock: {
    fontSize: 12,
    color: COLORS.gray,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  productRating: {
    fontSize: 12,
    color: COLORS.text,
  },
  productActions: {
    justifyContent: 'center',
    gap: 8,
  },
  actionBtn: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: COLORS.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
