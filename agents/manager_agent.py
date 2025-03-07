"""
管理智能体模块 - 负责任务分解、分配和结果整合
"""
import logging
from typing import List, Dict, Any
from agentlite.agents import ManagerAgent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MedicalManagerAgent(ManagerAgent):
    """
    医疗服务管理智能体
    
    负责将用户请求分解为子任务，分配给不同的个体智能体处理，
    并整合各个智能体的处理结果，生成最终响应。
    """
    
    def __init__(self, name: str, role: str, team_agents: List, llm):
        """
        初始化医疗服务管理智能体
        
        Args:
            name: 智能体名称
            role: 智能体角色描述
            team_agents: 团队中的个体智能体列表
        """
        super().__init__(name=name, role=role, TeamAgents=team_agents, llm=llm)
        logger.info(f"医疗管理智能体 {name} 已初始化，管理 {len(team_agents)} 个智能体")
    
    def decompose_task(self, instruction: str) -> List[Dict[str, Any]]:
        """
        将用户指令分解为多个子任务
        
        Args:
            instruction: 用户指令
            
        Returns:
            任务包列表，每个任务包包含分配给个体智能体的指令
        """
        logger.info(f"正在分解任务: {instruction}")
        
        # 任务分解逻辑
        # 这里简单示例，实际应用中可能需要更复杂的逻辑
        task_packages = []
        
        # 确定任务类型和需要的服务
        if "预约" in instruction or "挂号" in instruction:
            # 创建预约挂号任务
            for agent in self.TeamAgents:
                if "预约" in agent.role:
                    task_package = self._create_task_package(instruction, agent, "预约挂号")
                    task_packages.append(task_package)
                    logger.info(f"创建预约挂号任务，分配给智能体: {agent.name}")
                    
        elif "症状" in instruction or "诊断" in instruction:
            # 创建导诊推荐任务
            for agent in self.TeamAgents:
                if "导诊" in agent.role:
                    task_package = self._create_task_package(instruction, agent, "导诊推荐")
                    task_packages.append(task_package)
                    logger.info(f"创建导诊推荐任务，分配给智能体: {agent.name}")
                    
        elif "咨询" in instruction or "建议" in instruction:
            # 创建医疗咨询任务
            for agent in self.TeamAgents:
                if "咨询" in agent.role:
                    task_package = self._create_task_package(instruction, agent, "医疗咨询")
                    task_packages.append(task_package)
                    logger.info(f"创建医疗咨询任务，分配给智能体: {agent.name}")
                    
        else:
            # 默认将任务分配给所有智能体
            logger.info("无法确定具体任务类型，将分配给所有智能体处理")
            for agent in self.TeamAgents:
                task_package = self._create_task_package(instruction, agent, "通用任务")
                task_packages.append(task_package)
                
        return task_packages
    
    def _create_task_package(self, instruction: str, agent: Any, task_type: str) -> Dict[str, Any]:
        """
        创建任务包
        
        Args:
            instruction: 用户指令
            agent: 执行任务的智能体
            task_type: 任务类型
            
        Returns:
            任务包字典
        """
        return {
            "instruction": instruction,
            "task_type": task_type,
            "completion": "Incomplete",
            "creator": self.name,
            "timestamp": None,
            "answer": "",
            "executor": agent.name
        }
    
    def integrate_results(self, task_packages: List[Dict[str, Any]]) -> str:
        """
        整合各个智能体的处理结果，生成最终响应
        
        Args:
            task_packages: 任务包列表，每个任务包包含一个智能体的处理结果
            
        Returns:
            整合后的最终响应
        """
        logger.info(f"整合 {len(task_packages)} 个任务结果")
        
        # 简单整合示例
        results = []
        for package in task_packages:
            if package.get("completion") == "Completed":
                task_type = package.get("task_type", "未知任务")
                executor = package.get("executor", "未知智能体")
                answer = package.get("answer", "无结果")
                
                result = f"【{task_type} - {executor}】: {answer}"
                results.append(result)
                logger.info(f"添加结果: {task_type} 来自 {executor}")
        
        # 生成最终响应
        if results:
            final_response = "\n\n".join(results)
            logger.info("已成功整合所有任务结果")
        else:
            final_response = "抱歉，无法处理您的请求。请提供更多信息。"
            logger.warning("未找到任何完成的任务结果")
            
        return final_response
        
    def assign_tasks(self, instruction: str) -> str:
        """
        分配任务给团队中的智能体并获取结果
        
        Args:
            instruction: 用户指令
            
        Returns:
            整合后的响应
        """
        logger.info(f"开始处理用户指令: {instruction}")
        
        # 分解任务
        task_packages = self.decompose_task(instruction)
        
        # 分配任务给相应的智能体
        for task_package in task_packages:
            # 找到执行者
            executor_name = task_package["executor"]
            executor = None
            
            for agent in self.TeamAgents:
                if agent.name == executor_name:
                    executor = agent
                    break
            
            if executor:
                # 调用个体智能体执行任务
                logger.info(f"分配任务给 {executor_name}")
                prompt = executor.generate_prompt(task_package)
                action = executor.llm(prompt)
                result = executor.run_action(action)
                
                # 更新任务包
                task_package["answer"] = result
                task_package["completion"] = "Completed"
                logger.info(f"智能体 {executor_name} 已完成任务")
            else:
                logger.error(f"找不到执行者: {executor_name}")
                
        # 整合结果
        response = self.integrate_results(task_packages)
        logger.info("任务处理完成，返回最终响应")
        
        return response
