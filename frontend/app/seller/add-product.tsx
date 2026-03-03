import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
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

export default function AddProduct() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuth();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [originalPrice, setOriginalPrice] = useState('');
  const [stock, setStock] = useState('');
  const [categoryId, setCategoryId] = useState('');

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  const createMutation = useMutation({
    mutationFn: api.createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seller', 'products'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
      Alert.alert('Éxito', 'Producto creado correctamente', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    },
    onError: (error: any) => {
      Alert.alert('Error', error.message || 'No se pudo crear el producto');
    },
  });

  const handleSubmit = () => {
    if (!title.trim()) {
      Alert.alert('Error', 'El título es obligatorio');
      return;
    }
    if (!description.trim()) {
      Alert.alert('Error', 'La descripción es obligatoria');
      return;
    }
    if (!price || parseFloat(price) <= 0) {
      Alert.alert('Error', 'El precio debe ser mayor a 0');
      return;
    }
    if (!categoryId) {
      Alert.alert('Error', 'Selecciona una categoría');
      return;
    }

    createMutation.mutate({
      title: title.trim(),
      description: description.trim(),
      price: parseFloat(price),
      original_price: originalPrice ? parseFloat(originalPrice) : undefined,
      category_id: categoryId,
      stock: parseInt(stock) || 0,
      images: [],
    });
  };

  if (!isAuthenticated || user?.role !== 'seller') {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color={COLORS.white} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Añadir Producto</Text>
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
        <Text style={styles.headerTitle}>Añadir Producto</Text>
        <View style={{ width: 44 }} />
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Title */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Título *</Text>
            <TextInput
              style={styles.input}
              placeholder="Nombre del producto"
              placeholderTextColor={COLORS.gray}
              value={title}
              onChangeText={setTitle}
            />
          </View>

          {/* Description */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Descripción *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Describe tu producto"
              placeholderTextColor={COLORS.gray}
              value={description}
              onChangeText={setDescription}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />
          </View>

          {/* Price Row */}
          <View style={styles.row}>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Precio *</Text>
              <TextInput
                style={styles.input}
                placeholder="0.00"
                placeholderTextColor={COLORS.gray}
                value={price}
                onChangeText={setPrice}
                keyboardType="decimal-pad"
              />
            </View>
            <View style={{ width: 16 }} />
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Precio original</Text>
              <TextInput
                style={styles.input}
                placeholder="0.00"
                placeholderTextColor={COLORS.gray}
                value={originalPrice}
                onChangeText={setOriginalPrice}
                keyboardType="decimal-pad"
              />
            </View>
          </View>

          {/* Stock */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Stock disponible</Text>
            <TextInput
              style={styles.input}
              placeholder="0"
              placeholderTextColor={COLORS.gray}
              value={stock}
              onChangeText={setStock}
              keyboardType="number-pad"
            />
          </View>

          {/* Category */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Categoría *</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryScroll}>
              {categories?.map((category: any) => (
                <TouchableOpacity
                  key={category.category_id}
                  style={[
                    styles.categoryChip,
                    categoryId === category.category_id && styles.categoryChipSelected,
                  ]}
                  onPress={() => setCategoryId(category.category_id)}
                >
                  <Ionicons
                    name={category.icon as any}
                    size={16}
                    color={categoryId === category.category_id ? COLORS.white : category.color}
                  />
                  <Text
                    style={[
                      styles.categoryChipText,
                      categoryId === category.category_id && styles.categoryChipTextSelected,
                    ]}
                  >
                    {category.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitBtn, createMutation.isPending && styles.submitBtnDisabled]}
            onPress={handleSubmit}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? (
              <ActivityIndicator color={COLORS.white} />
            ) : (
              <>
                <Ionicons name="add-circle" size={22} color={COLORS.white} />
                <Text style={styles.submitBtnText}>Publicar Producto</Text>
              </>
            )}
          </TouchableOpacity>

          <View style={{ height: 100 }} />
        </ScrollView>
      </KeyboardAvoidingView>
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
    paddingTop: 20,
    paddingHorizontal: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.gray,
    marginTop: 16,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  input: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: COLORS.text,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  textArea: {
    minHeight: 100,
    paddingTop: 16,
  },
  row: {
    flexDirection: 'row',
  },
  categoryScroll: {
    flexDirection: 'row',
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 10,
    gap: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  categoryChipSelected: {
    backgroundColor: COLORS.accent,
  },
  categoryChipText: {
    fontSize: 13,
    color: COLORS.text,
    fontWeight: '500',
  },
  categoryChipTextSelected: {
    color: COLORS.white,
  },
  submitBtn: {
    flexDirection: 'row',
    backgroundColor: COLORS.accent,
    borderRadius: 14,
    padding: 18,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    marginTop: 12,
  },
  submitBtnDisabled: {
    opacity: 0.7,
  },
  submitBtnText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: '700',
  },
});
