import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../src/services/api';
import { ProductCard } from '../src/components/ProductCard';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
};

export default function SearchScreen() {
  const router = useRouter();
  const { q } = useLocalSearchParams<{ q: string }>();
  const [searchQuery, setSearchQuery] = useState(q || '');

  const { data: productsData, isLoading, refetch } = useQuery({
    queryKey: ['products', 'search', searchQuery],
    queryFn: () => api.getProducts({ search: searchQuery }),
    enabled: searchQuery.length > 0,
  });

  const handleSearch = () => {
    if (searchQuery.trim()) {
      refetch();
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
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
            autoFocus
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={20} color={COLORS.gray} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.content}>
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={COLORS.accent} />
          </View>
        ) : !searchQuery ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="search-outline" size={60} color={COLORS.gray} />
            <Text style={styles.emptyText}>Busca productos por nombre</Text>
          </View>
        ) : productsData?.products?.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="sad-outline" size={60} color={COLORS.gray} />
            <Text style={styles.emptyText}>No se encontraron resultados para "{searchQuery}"</Text>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={styles.resultCount}>
              {productsData?.total || 0} resultados para "{searchQuery}"
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
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 12,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBar: {
    flex: 1,
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
