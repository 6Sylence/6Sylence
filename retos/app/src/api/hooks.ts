/** Hooks de datos. Toda llamada pasa por aquí para no dispersar el token. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { useSession } from '../context/SessionContext';
import { request } from './client';
import type {
  AgeBand,
  Child,
  Milestone,
  ParentProfile,
  PlanView,
  WeekView,
} from './types';

export const queryKeys = {
  parent: ['parent'] as const,
  children: ['children'] as const,
  plan: (childId: string) => ['plan', childId] as const,
  week: (childId: string, weekIndex: number | 'current') =>
    ['week', childId, weekIndex] as const,
  milestones: (childId: string) => ['milestones', childId] as const,
};

export function useParent() {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.parent,
    enabled: !!token,
    queryFn: () => request<ParentProfile>('/auth/me', { token }),
  });
}

export function useChildren() {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.children,
    enabled: !!token,
    queryFn: () => request<Child[]>('/children', { token }),
  });
}

export function useCreateChild() {
  const { token } = useSession();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string; age_band: AgeBand; avatar_key: string }) =>
      request<Child>('/children', { method: 'POST', body: input, token }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.children }),
  });
}

export function usePlan(childId: string | null) {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.plan(childId ?? ''),
    enabled: !!token && !!childId,
    queryFn: () => request<PlanView>(`/children/${childId}/plan`, { token }),
  });
}

export function useCurrentWeek(childId: string | null) {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.week(childId ?? '', 'current'),
    enabled: !!token && !!childId,
    queryFn: () => request<WeekView>(`/children/${childId}/weeks/current`, { token }),
  });
}

export function useWeek(childId: string | null, weekIndex: number | null) {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.week(childId ?? '', weekIndex ?? 0),
    enabled: !!token && !!childId && !!weekIndex,
    queryFn: () => request<WeekView>(`/children/${childId}/weeks/${weekIndex}`, { token }),
  });
}

/** Invalida todo lo que depende del progreso de un niño. */
function useProgressInvalidation(childId: string | null) {
  const queryClient = useQueryClient();
  return () => {
    if (!childId) return;
    queryClient.invalidateQueries({ queryKey: ['week', childId] });
    queryClient.invalidateQueries({ queryKey: queryKeys.plan(childId) });
    queryClient.invalidateQueries({ queryKey: queryKeys.milestones(childId) });
  };
}

export function useCompleteActivity(childId: string | null, weekIndex: number | null) {
  const { token } = useSession();
  const invalidate = useProgressInvalidation(childId);
  return useMutation({
    mutationFn: (activityId: string) =>
      request<WeekView>(
        `/children/${childId}/weeks/${weekIndex}/activities/${activityId}/complete`,
        // El cuerpo solo lleva la confirmación del adulto. Nunca una imagen.
        { method: 'POST', body: { validated_by_parent: true }, token },
      ),
    onSuccess: invalidate,
  });
}

export function useUndoActivity(childId: string | null, weekIndex: number | null) {
  const { token } = useSession();
  const invalidate = useProgressInvalidation(childId);
  return useMutation({
    mutationFn: (activityId: string) =>
      request<WeekView>(
        `/children/${childId}/weeks/${weekIndex}/activities/${activityId}/complete`,
        { method: 'DELETE', token },
      ),
    onSuccess: invalidate,
  });
}

export function useChooseReward(childId: string | null, weekIndex: number | null) {
  const { token } = useSession();
  const invalidate = useProgressInvalidation(childId);
  return useMutation({
    mutationFn: (optionId: string) =>
      request<WeekView>(`/children/${childId}/weeks/${weekIndex}/reward`, {
        method: 'POST',
        body: { option_id: optionId },
        token,
      }),
    onSuccess: invalidate,
  });
}

export function useMilestones(childId: string | null) {
  const { token } = useSession();
  return useQuery({
    queryKey: queryKeys.milestones(childId ?? ''),
    enabled: !!token && !!childId,
    queryFn: () => request<Milestone[]>(`/children/${childId}/milestones`, { token }),
  });
}
