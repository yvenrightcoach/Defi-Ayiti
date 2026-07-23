import { apiClient } from "@/services/apiClient";
import type { Department, DepartmentDetail, Level, Paginated } from "@/types/api";

export async function listDepartments(): Promise<Department[]> {
  const { data } = await apiClient.get<Paginated<Department>>("/geography/departments/", {
    params: { page_size: 20 },
  });
  return data.results;
}

export async function getDepartment(id: string): Promise<DepartmentDetail> {
  const { data } = await apiClient.get<DepartmentDetail>(`/geography/departments/${id}/`);
  return data;
}

export async function listLevels(departmentId: string): Promise<Level[]> {
  const { data } = await apiClient.get<Paginated<Level>>("/geography/levels/", {
    params: { department: departmentId, page_size: 50 },
  });
  return data.results;
}
