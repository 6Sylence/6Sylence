import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../src/services/api';
import { ProductCard } from '../../src/components/ProductCard';
import { CategoryCard } from '../../src/components/CategoryCard';

const { width } = Dimensions.get('window');

const COLORS = {
  primary: '#1A1A2E',
  secondary: '#16213E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
};

export default function HomeScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const { data: categories, isLoading: loadingCategories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  const { data: featuredProducts, isLoading: loadingFeatured, refetch: refetchFeatured } = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: () => api.getProducts({ featured: true }),
  });

  const { data: allProducts, isLoading: loadingAll, refetch: refetchAll } = useQuery({
    queryKey: ['products', 'all'],
    queryFn: () => api.getProducts({ limit: 20 }),
  });

  // Seed data on first load
  useEffect(() => {
    const seedData = async () => {
      try {
        await api.seedData();
      } catch (error) {
        console.log('Seed already done or error:', error);
      }
    };
    seedData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchFeatured(), refetchAll()]);
    setRefreshing(false);
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const isLoading = loadingCategories || loadingFeatured || loadingAll;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Ionicons name="storefront" size={28} color={COLORS.gold} />
          <Text style={styles.logoText}>MarketPro</Text>
        </View>
        <TouchableOpacity style={styles.notificationBtn}>
          <Ionicons name="notifications-outline" size={24} color={COLORS.white} />
        </TouchableOpacity>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color={COLORS.gray} />
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar productos..."
            placeholderTextColor={COLORS.gray}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={20} color={COLORS.gray} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.accent} />
        }
      >
        {/* Categories Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Categorías</Text>
            <TouchableOpacity onPress={() => router.push('/(tabs)/categories')}>
              <Text style={styles.seeAll}>Ver todas</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoriesScroll}>
            {loadingCategories ? (
              <ActivityIndicator color={COLORS.accent} style={{ paddingHorizontal: 20 }} />
            ) : (
              categories?.slice(0, 8).map((category: any) => (
                <CategoryCard
                  key={category.category_id}
                  category={category}
                  onPress={() => router.push(`/category/${category.category_id}`)}
                />
              ))
            )}
          </ScrollView>
        </View>

        {/* Featured Products */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.featuredBadge}>
              <Ionicons name="star" size={16} color={COLORS.gold} />
              <Text style={styles.sectionTitle}>Destacados</Text>
            </View>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.productsScroll}>
            {loadingFeatured ? (
              <ActivityIndicator color={COLORS.accent} style={{ paddingHorizontal: 20 }} />
            ) : (
              featuredProducts?.products?.map((product: any) => (
                <ProductCard
                  key={product.product_id}
                  product={product}
                  onPress={() => router.push(`/product/${product.product_id}`)}
                  horizontal
                />
              ))
            )}
          </ScrollView>
        </View>

        {/* All Products */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Productos populares</Text>
          </View>
          <View style={styles.productsGrid}>
            {loadingAll ? (
              <ActivityIndicator color={COLORS.accent} style={{ padding: 40 }} />
            ) : (
              allProducts?.products?.map((product: any) => (
                <ProductCard
                  key={product.product_id}
                  product={product}
                  onPress={() => router.push(`/product/${product.product_id}`)}
                />
              ))
            )}
          </View>
        </View>

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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  logoText: {
    fontSize: 22,
    fontWeight: '700',
    color: COLORS.white,
  },
  notificationBtn: {
    padding: 8,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 48,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: COLORS.text,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  section: {
    paddingTop: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.text,
  },
  seeAll: {
    fontSize: 14,
    color: COLORS.accent,
    fontWeight: '600',
  },
  featuredBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  categoriesScroll: {
    paddingLeft: 16,
  },
  productsScroll: {
    paddingLeft: 16,
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
    justifyContent: 'space-between',
  },
});
