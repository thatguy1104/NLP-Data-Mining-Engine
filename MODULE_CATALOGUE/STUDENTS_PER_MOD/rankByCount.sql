SELECT ModuleData.Module_Name,
    StudentsPerModule.ModuleID,
    StudentsPerModule.NumberOfStudents,
    StudentsPerModule.Last_Updated FROM [dbo].[StudentsPerModule]
INNER JOIN [dbo].[ModuleData] ON StudentsPerModule.ModuleID = ModuleData.Module_ID
ORDER BY StudentsPerModule.NumberOfStudents DESC