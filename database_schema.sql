-- 汇报评分投票系统数据库设计
-- 创建数据库
CREATE DATABASE IF NOT EXISTS voting_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE voting_system;

-- 1. 汇报项目表
CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '汇报标题',
    description TEXT COMMENT '汇报描述/内容',
    creator VARCHAR(100) NOT NULL COMMENT '创建者姓名',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    status ENUM('active', 'closed') DEFAULT 'active' COMMENT '投票状态',
    deadline DATETIME COMMENT '投票截止时间'
);

-- 2. 评委表
CREATE TABLE judges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '评委姓名',
    email VARCHAR(255) COMMENT '邮箱',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 投票记录表
CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT NOT NULL COMMENT '汇报项目ID',
    judge_name VARCHAR(100) NOT NULL COMMENT '评委姓名',
    score INT NOT NULL COMMENT '评分(-3到3)',
    comment TEXT COMMENT '评价意见',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '投票时间',
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    UNIQUE KEY unique_vote (report_id, judge_name) COMMENT '同一评委对同一汇报只能投票一次'
);

-- 4. 汇报结果汇总视图
CREATE VIEW report_results AS
SELECT 
    r.id,
    r.title,
    r.description,
    r.creator,
    r.created_at,
    r.status,
    COUNT(v.id) as vote_count,
    COALESCE(AVG(v.score), 0) as avg_score,
    COALESCE(AVG(v.score), 0) + 5 as total_score,
    GROUP_CONCAT(CONCAT(v.judge_name, ':', v.score, '分') SEPARATOR '; ') as score_details
FROM reports r
LEFT JOIN votes v ON r.id = v.report_id
GROUP BY r.id, r.title, r.description, r.creator, r.created_at, r.status;

-- 插入一些示例评委数据
INSERT INTO judges (name, email) VALUES 
('张三', 'zhangsan@company.com'),
('李四', 'lisi@company.com'),
('王五', 'wangwu@company.com'),
('赵六', 'zhaoliu@company.com');

-- 创建索引优化查询性能
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_votes_report_id ON votes(report_id);
CREATE INDEX idx_votes_judge_name ON votes(judge_name);