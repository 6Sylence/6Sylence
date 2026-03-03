import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 48) / 2;
const HORIZONTAL_CARD_WIDTH = width * 0.6;

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
};

interface Product {
  product_id: string;
  title: string;
  price: number;
  original_price?: number;
  images?: string[];
  rating: number;
  review_count: number;
  stock: number;
  featured?: boolean;
}

interface ProductCardProps {
  product: Product;
  onPress: () => void;
  horizontal?: boolean;
}

export function ProductCard({ product, onPress, horizontal = false }: ProductCardProps) {
  const discount = product.original_price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  const imageUrl = product.images && product.images.length > 0 ? product.images[0] : null;

  return (
    <TouchableOpacity
      style={[styles.container, horizontal && styles.horizontalContainer]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      {/* Product Image */}
      <View style={[styles.imageContainer, horizontal && styles.horizontalImage]}>
        {imageUrl ? (
          <Image 
            source={{ uri: imageUrl }} 
            style={styles.productImage}
            resizeMode="cover"
          />
        ) : (
          <Ionicons name="cube-outline" size={40} color={COLORS.gray} />
        )}
        {discount > 0 && (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>-{discount}%</Text>
          </View>
        )}
        {product.featured && (
          <View style={styles.featuredBadge}>
            <Ionicons name="star" size={12} color={COLORS.gold} />
          </View>
        )}
      </View>

      {/* Product Info */}
      <View style={styles.infoContainer}>
        <Text style={styles.title} numberOfLines={2}>{product.title}</Text>
        
        <View style={styles.ratingContainer}>
          <Ionicons name="star" size={14} color={COLORS.gold} />
          <Text style={styles.rating}>{product.rating.toFixed(1)}</Text>
          <Text style={styles.reviewCount}>({product.review_count})</Text>
        </View>

        <View style={styles.priceContainer}>
          <Text style={styles.price}>€{product.price.toFixed(2)}</Text>
          {product.original_price && (
            <Text style={styles.originalPrice}>€{product.original_price.toFixed(2)}</Text>
          )}
        </View>

        {product.stock <= 5 && product.stock > 0 && (
          <Text style={styles.lowStock}>¡Solo quedan {product.stock}!</Text>
        )}
        {product.stock === 0 && (
          <Text style={styles.outOfStock}>Agotado</Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    width: CARD_WIDTH,
    backgroundColor: COLORS.white,
    borderRadius: 16,
    marginHorizontal: 8,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
    overflow: 'hidden',
  },
  horizontalContainer: {
    width: HORIZONTAL_CARD_WIDTH,
    marginRight: 16,
    marginBottom: 0,
  },
  imageContainer: {
    height: 140,
    backgroundColor: COLORS.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  horizontalImage: {
    height: 120,
  },
  discountBadge: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: COLORS.accent,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  discountText: {
    color: COLORS.white,
    fontSize: 11,
    fontWeight: '700',
  },
  featuredBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: COLORS.white,
    padding: 4,
    borderRadius: 12,
  },
  infoContainer: {
    padding: 12,
  },
  title: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.text,
    lineHeight: 18,
    minHeight: 36,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    gap: 4,
  },
  rating: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.text,
  },
  reviewCount: {
    fontSize: 11,
    color: COLORS.gray,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 8,
  },
  price: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.accent,
  },
  originalPrice: {
    fontSize: 13,
    color: COLORS.gray,
    textDecorationLine: 'line-through',
  },
  lowStock: {
    fontSize: 11,
    color: '#FF9800',
    fontWeight: '600',
    marginTop: 6,
  },
  outOfStock: {
    fontSize: 11,
    color: COLORS.accent,
    fontWeight: '600',
    marginTop: 6,
  },
});
