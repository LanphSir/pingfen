# competition documentation
## Summary

- [Introduction](#introduction)
- [Database Type](#database-type)
- [Table Structure](#table-structure)
	- [competition](#competition)
	- [project](#project)
	- [evaluation_dimension](#evaluation_dimension)
	- [evaluation_grade](#evaluation_grade)
	- [judge](#judge)
	- [judge_assignment](#judge_assignment)
	- [evaluation_record](#evaluation_record)
	- [participant](#participant)
	- [entry](#entry)
	- [entry_participant](#entry_participant)
	- [organization](#organization)
- [Relationships](#relationships)
- [Database Diagram](#database-diagram)

## Introduction

## Database type

- **Database system:** SQLite
## Table structure

### competition
比赛表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **name** | TEXT(100) | not null |  |比赛名称 |
| **start_time** | TEXT(65535) | not null |  |开始时间 |
| **end_time** | TEXT(65535) | not null |  |结束时间 |
| **description** | TEXT(65535) | null |  |比赛描述 | 


### project
项目表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **competition_id** | INTEGER | null | fk_project_competition_id_competition |所属比赛 ID |
| **name** | TEXT(100) | not null |  |项目名称 |
| **type** | TEXT(100) | null |  |项目类型（AI 内容创作类 / 系统开发类） |
| **description** | TEXT(65535) | null |  |项目描述 | 


### evaluation_dimension
评分维度表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **project_id** | INTEGER | null | fk_evaluation_dimension_project_id_project |所属项目 ID |
| **name** | TEXT(100) | not null |  |维度名称（如 “技术实现度”） |
| **weight** | INTEGER | not null |  |维度权重（分值） |
| **description** | TEXT(65535) | null |  |评分维度描述 | 


### evaluation_grade
评分档位
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **dimension_id** | INTEGER | not null | fk_evaluation_grade_dimension_id_evaluation_dimension | |
| **score** | INTEGER | not null |  |档位分数（5/10/15 等） |
| **description** | TEXT(65535) | null |  |档位说明 | 


### judge
评分人员表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **name** | TEXT(100) | not null |  |姓名 |
| **account** | TEXT(100) | null |  |账号（登录用） |
| **role** | TEXT(100) | null |  |角色（如 “专家评委”） |
| **contact** | TEXT(100) | null |  |联系方式 |
| **organization_id** | INTEGER | null | fk_judge_organization_id_organization |学校/组织ID |
| **remark** | TEXT(65535) | null |  |备注 | 


### judge_assignment
评分（任务）分配表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **judge_id** | INTEGER | null | fk_judge_assignment_judge_id_judge |评分人员 ID |
| **project_id** | INTEGER | null | fk_judge_assignment_project_id_project |项目 ID |
| **assign_time** | TEXT(65535) | null |  |分配时间 |
| **remark** | TEXT(65535) | null |  |备注 | 


### evaluation_record
评分记录表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **entry_id** | INTEGER | null | fk_evaluation_record_entry_id_entry_participant |作品 ID（关联 entry 表） |
| **project_id** | INTEGER | null | fk_evaluation_record_project_id_project |项目 ID（关联 project 表） |
| **dimension_id** | INTEGER | null | fk_evaluation_record_dimension_id_evaluation_dimension |评分维度 ID（关联 evaluation_dimension 表） |
| **judge_id** | INTEGER | null | fk_evaluation_record_judge_id_judge |评分人员 ID（关联 judge 表） |
| **score** | INTEGER | null |  |得分 |
| **score_time** | TEXT(65535) | null |  |评分时间 | 


### participant
 参赛人表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **name** | TEXT(100) | not null |  | |
| **account** | TEXT(100) | null |  |账号（用于提交作品） |
| **contact** | TEXT(100) | not null |  |联系方式（手机 / 邮箱） |
| **organization_id** | INTEGER | not null | fk_participant_organization_id_organization |所属单位 / 学校ID |
| **is_team** | INTEGER | not null, default: 0 |  |是否为团队 |
| **remake** | TEXT(65535) | null |  |备注 | 


### entry
作品表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **title** | TEXT(100) | not null |  |作品标题 |
| **project_id** | INTEGER | null | fk_entry_participant_project_id_project |所属项目 ID |
| **url** | TEXT(100) | not null |  |作品存储路径 |
| **type** | TEXT(100) | null |  |作品类型 |
| **description** | TEXT(65535) | null |  |作品简介 |
| **submit_time** | TEXT(65535) | null |  |提交时间 |
| **review_status** | INTEGER | not null, default: 0 |  |审核状态（0 = 待审核，1 = 通过，2 = 驳回） |
| **review_remark** | TEXT(65535) | null |  |审核备注（驳回原因等） |
| **score** | NUMERIC(11,2) | null |  |作品得分 | 


### entry_participant
作品 - 参赛人关联表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **entry_id** | INTEGER | null | fk_entry_participant_entry_id_entry |作品 ID |
| **participant_id** | INTEGER | null | fk_entry_participant_participant_id_participant |参赛人 ID |
| **is_leader** | INTEGER | null, default: 0 |  | | 


### organization
组织/学校表
| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | INTEGER | 🔑 PK, not null, unique, autoincrement |  | |
| **name** | TEXT(100) | not null |  |组织/学校名称 |
| **department** | TEXT(100) | null |  |二级院校（院系） |
| **remark** | TEXT(65535) | null |  |备注 | 


## Relationships

- **entry to project**: one_to_one
- **evaluation_grade to evaluation_dimension**: one_to_one
- **evaluation_dimension to project**: many_to_one
- **judge_assignment to project**: one_to_one
- **judge_assignment to judge**: one_to_one
- **evaluation_record to entry**: many_to_one
- **evaluation_record to project**: one_to_one
- **evaluation_record to evaluation_dimension**: one_to_one
- **evaluation_record to judge**: one_to_many
- **project to competition**: one_to_one
- **entry_participant to entry**: many_to_one
- **entry_participant to participant**: many_to_one
- **judge to organization**: many_to_one
- **participant to organization**: many_to_one

## Database Diagram

```mermaid
erDiagram
	entry ||--|| project : references
	evaluation_grade ||--|| evaluation_dimension : references
	evaluation_dimension }o--|| project : references
	judge_assignment ||--|| project : references
	judge_assignment ||--|| judge : references
	evaluation_record }o--|| entry : references
	evaluation_record ||--|| project : references
	evaluation_record ||--|| evaluation_dimension : references
	evaluation_record ||--o{ judge : references
	project ||--|| competition : references
	entry_participant }o--|| entry : references
	entry_participant }o--|| participant : references
	judge }o--|| organization : references
	participant }o--|| organization : references

	competition {
		INTEGER id
		TEXT(100) name
		TEXT(65535) start_time
		TEXT(65535) end_time
		TEXT(65535) description
	}

	project {
		INTEGER id
		INTEGER competition_id
		TEXT(100) name
		TEXT(100) type
		TEXT(65535) description
	}

	evaluation_dimension {
		INTEGER id
		INTEGER project_id
		TEXT(100) name
		INTEGER weight
		TEXT(65535) description
	}

	evaluation_grade {
		INTEGER id
		INTEGER dimension_id
		INTEGER score
		TEXT(65535) description
	}

	judge {
		INTEGER id
		TEXT(100) name
		TEXT(100) account
		TEXT(100) role
		TEXT(100) contact
		INTEGER organization_id
		TEXT(65535) remark
	}

	judge_assignment {
		INTEGER id
		INTEGER judge_id
		INTEGER project_id
		TEXT(65535) assign_time
		TEXT(65535) remark
	}

	evaluation_record {
		INTEGER id
		INTEGER entry_id
		INTEGER project_id
		INTEGER dimension_id
		INTEGER judge_id
		INTEGER score
		TEXT(65535) score_time
	}

	participant {
		INTEGER id
		TEXT(100) name
		TEXT(100) account
		TEXT(100) contact
		INTEGER organization_id
		INTEGER is_team
		TEXT(65535) remake
	}

	entry {
		INTEGER id
		TEXT(100) title
		INTEGER project_id
		TEXT(100) url
		TEXT(100) type
		TEXT(65535) description
		TEXT(65535) submit_time
		INTEGER review_status
		TEXT(65535) review_remark
		NUMERIC(11,2) score
	}

	entry_participant {
		INTEGER id
		INTEGER entry_id
		INTEGER participant_id
		INTEGER is_leader
	}

	organization {
		INTEGER id
		TEXT(100) name
		TEXT(100) department
		TEXT(65535) remark
	}
```