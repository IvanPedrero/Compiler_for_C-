.text
   .globl main

   gcd:                 # Function declaration
        sw $ra 0($sp)
        addiu $sp $sp -4
        move $fp $sp
        addiu $sp $sp 8
        lw $a0 0($sp)
        sw $a0 0($fp)
        addiu $sp $sp -4
        addiu $sp $sp -4
        addiu $sp $sp -4
        addiu $sp $sp -4
        sw $a0 4($fp)
        sw $a0 0($sp)
        addiu $sp $sp -4
        li $a0 0
        lw $t5 4($sp)
        addiu $sp $sp 4
        beq $a0 $t5 if_true_branch_0		# == comparison
        if_false_branch_0:
        sw $fp 0($sp)
        addiu $sp $sp -4
        lw $a0 4($fp)
        sw $a0 0($sp)
        addiu $sp $sp -4
        sw $a0 0($sp)
        addiu $sp $sp -4
        jal gcd                 # Call to function
        b end_if_0
        if_true_branch_0:
        sw $a0 4($fp)
        sw $a0 0($sp)
        addiu $sp $sp -4
        li $a0 0
        lw $t5 4($sp)
        addiu $sp $sp 4
        end_if_0:
        sw $a0 0($fp)
        lw $ra 4($fp)
        addiu $sp $sp 20
        lw $fp 0($sp)
        jr $ra

   main:                 # Driver function
        la $t4 stack
        move $fp $sp
        addiu $sp $sp -8
        li $v0 5 
        syscall 
        move $a0 $v0 
        sw $a0 0($fp)
        li $v0 5 
        syscall 
        move $a0 $v0 
        sw $a0 0($fp)
        sw $fp 0($sp)
        addiu $sp $sp -4
        lw $a0 -4($fp)
        sw $a0 0($sp)
        addiu $sp $sp -4
        lw $a0 -8($fp)
        sw $a0 0($sp)
        addiu $sp $sp -4
        jal gcd                 # Call to function
        li $v0 1 
        syscall 


.data
   stack: .word 0		# $t4 for stack, $t5 and $t6 for arithmetic/logic operations
