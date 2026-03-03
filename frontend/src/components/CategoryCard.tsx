import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const COLORS = {
  white: '#FFFFFF',
  text: '#333333',
};

interface Category {
  category_id: string;
  name: string;
  icon: string;
  color: string;
}

interface CategoryCardProps {
  category: Category;
  onPress: () => void;
}

export function CategoryCard({ category, onPress }: CategoryCardProps) {
  return (
    <TouchableOpacity style={styles.container} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.iconContainer, { backgroundColor: category.color + '20' }]}>
        <Ionicons name={category.icon as any} size={28} color={category.color} />
      </View>
      <Text style={styles.name} numberOfLines={1}>{category.name}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginRight: 16,
    width: 80,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  name: {
    fontSize: 12,
    fontWeight: '500',
    color: COLORS.text,
    marginTop: 8,
    textAlign: 'center',
  },
});
