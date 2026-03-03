import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../src/services/api';
import { ProductCard } from '../../src/components/ProductCard';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
};

export default function CategoryScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  const category = categories?.find((c: any) => c.category_id === id);

  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products', 'category', id],
    queryFn: () => api.getProducts({ category_id: id }),
    enabled: !!id,
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          {category && (
            <Ionicons name={category.icon as any} size={24} color={category.color} />
          )}
          <Text style={styles.headerTitle}>{category?.name || 'Categoría'}</Text>
        </View>
        <View style={{ width: 44 }} />
      </View>

      <View style={styles.content}>
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={COLORS.accent} />
          </View>
        ) : productsData?.products?.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="cube-outline" size={60} color={COLORS.gray} />
            <Text style={styles.emptyText}>No hay productos en esta categoría</Text>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={styles.resultCount}>
              {productsData?.total || 0} productos encontrados
            </Text>
            <View style={styles.productsGrid}>
              {productsData?.products?.map((product: any) => (
                <ProductCard
                  key={product.product_id}
                  product={product}
                  onPress={() => router.push(`/product/${product.product_id}`)}
                />
              ))}
            </View>
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
  headerTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
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
  resultCount: {
    fontSize: 14,
    color: COLORS.gray,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 12,
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
    justifyContent: 'space-between',
  },
});
